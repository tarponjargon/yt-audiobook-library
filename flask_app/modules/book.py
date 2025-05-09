import re
from flask_app.modules.helpers import (
    string_to_ascii,
    html_entities_to_chars,
    trim_and_reduce_whitespace,
)
from datetime import timedelta # Added import
from flask_app.modules.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flask_app.models import Audiobook, SkippedVideo, Category, Author # Added Author import


# Modify store_book_info to use the updated Audiobook model
def store_book_info(book_data):
    """
    Stores the processed book data into the database using SQLAlchemy,
    checking for duplicate video_id.

    Args:
        book_data (dict): A dictionary containing the processed book details
                          (video_id, title, description, thumbnail, author, categories, duration).

    Returns:
        bool: True if the book was added, False otherwise.
    """
    try:
        video_id = book_data.get("video_id")
        if not video_id:
            print("\tError: Missing video_id in book data.")
            return False

        # --- Create new Audiobook object ---
        new_audiobook = Audiobook(
            video_id=video_id,
            title=book_data.get("title"),
            description=book_data.get("description"),
            thumbnail=book_data.get("thumbnail"),
            # author=book_data.get("author"), # Author is now handled via relationship
            duration=book_data.get("duration"),
            # timestamp is handled by the model default
        )

        # --- Handle Author ---
        author_name = book_data.get("author")
        author_instance = None
        if author_name:
            # Find existing author or create a new one
            author_instance = db.session.execute(
                db.select(Author).filter_by(name=author_name)
            ).scalar_one_or_none()
            if not author_instance:
                author_instance = Author(name=author_name)
                db.session.add(author_instance)
                # Flush to get the author ID if needed immediately, or commit handles it
                # db.session.flush()
            # Associate the author with the audiobook
            new_audiobook.author = author_instance
        # --- End Handle Author ---


        # Add the audiobook to the session BEFORE handling categories
        db.session.add(new_audiobook)

        # --- Handle Categories ---
        category_names = book_data.get("categories", [])
        if category_names:
            for cat_name in category_names:
                # Find existing category or create a new one
                category = db.session.execute(
                    db.select(Category).filter_by(name=cat_name)
                ).scalar_one_or_none()
                if not category:
                    category = Category(name=cat_name)
                    db.session.add(category)
                    # Flush to get the category ID if needed, or commit handles it
                    # db.session.flush()
                # Append the category object to the audiobook's categories list
                if category not in new_audiobook.categories:
                    new_audiobook.categories.append(category)
        # --- End Handle Categories ---

        # Commit the session (includes audiobook and any new categories)
        db.session.commit()
        duration_msg = (
            f"(Duration: {new_audiobook.duration}s)"
            if new_audiobook.duration is not None
            else "(Duration: Unknown)"
        )
        author_display = new_audiobook.author.name if new_audiobook.author else "Unknown"
        print(f"Stored: Title '{new_audiobook.title}' Author: {author_display}")
        return True

    except Exception as e:  # Catch potential DB errors or other issues
        db.session.rollback()  # Rollback transaction on error
        print(f"Error storing book for video ID '{video_id}': {e}")
        return False


def check_if_book_exists(video_id):
    # Use .unique() because Audiobook uses joined eager loading for categories
    found = (
        db.session.execute(db.select(Audiobook).filter_by(video_id=video_id))
        .unique()
        .scalar_one_or_none()
    )

    if not found:
        # Check if the video is in the skipped videos table
        found = db.session.execute(
            db.select(SkippedVideo).filter_by(video_id=video_id)
        ).scalar_one_or_none()

    return found


def ineligible_video(video_id, reason):
    """
    Store the ineligible video in the database
    """
    try:
        # Let the database handle the timestamp via server_default
        new_skipped_video = SkippedVideo(
            video_id=video_id,
            reason=reason,
        )
        db.session.add(new_skipped_video)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"\tError storing skipped video '{video_id}': {e}")
        return False

    print(f"\tSkipped: {video_id} - {reason}")
    return True


def remove_extra_terms(input_string):
    """
    Removes specific audiobook-related terms from the input string.

    Args:
        input_string (str): The string to process.

    Returns:
        str: The string with audiobook terms removed.
    """
    audiobook_terms = [
        "(full audiobook)",
        "(free audiobook)",
        "(complete audiobook)",
        "full audiobook",
        "free audiobook",
        "complete audiobook",
        "(audiobook)",
        "audiobook",
    ]
    for term in audiobook_terms:
        input_string = re.sub(re.escape(term), "", input_string, flags=re.IGNORECASE)

    # Remove hashtags and any commas immediately following them
    input_string = re.sub(r"#\w+,?", "", input_string, flags=re.IGNORECASE)

    # if the string ens with a - or a | or a , with an optional space before or after, remove it
    input_string = re.sub(r"\s?[-\|,]\s?$", "", input_string)

    # print(f"Processed string: {input_string}")

    return input_string


def process_book_name(input_string):
    """
    Processes the input string by applying the following functions in order:
    1. split_pipe_remove_last
    2. html_entities_to_chars
    3. remove_extra_terms
    4. string_to_ascii
    5. trim_and_reduce_whitespace

    Args:
        input_string (str): The string to process.

    Returns:
        str: The fully processed string.
    """
    processed = input_string
    # processed = split_pipe_remove_last(processed)
    processed = html_entities_to_chars(processed)
    processed = string_to_ascii(processed)
    processed = remove_extra_terms(processed)
    processed = trim_and_reduce_whitespace(processed)
    return processed


def split_pipe_remove_last(input_string):
    """
    Splits a string by the pipe character and removes the last element if the list has more than one element.
    Then, converts the list back to a string.

    Args:
        input_string (str): The string to be split and modified.

    Returns:
        str: The modified string after removing the last element, or the original string if no removal was needed.
    """
    parts = input_string.split("|")
    if len(parts) > 1:
        parts.pop()
        return "|".join(parts)
    return input_string


def parse_iso8601_duration(duration_str):
    """Parses an ISO 8601 duration string (e.g., P1DT1H2M3S) into total seconds."""
    if not duration_str or not duration_str.startswith("P"):
        print(f"\tWarning: Invalid duration format (missing P): {duration_str}")
        return None

    # Regex to capture days, hours, minutes, seconds
    # Handles P<date>T<time>, PT<time>, P<date>
    # Ignores weeks (W) and months/years (not typically used by YouTube)
    match = re.match(
        r"P"  # Starts with P
        r"(?:(\d+)D)?"  # Optional Days
        r"(?:T"  # Optional Time part starts with T
        r"(?:(\d+)H)?"  # Optional Hours
        r"(?:(\d+)M)?"  # Optional Minutes
        r"(?:(\d+)S)?"  # Optional Seconds
        r")?",  # End of optional Time part
        duration_str,
    )

    if not match:
        # Handle cases like PT0S which is valid but the regex might miss if T is mandatory
        if duration_str == "PT0S":
            return 0
        print(f"\tWarning: Could not parse ISO 8601 duration format: {duration_str}")
        return None

    days_str, hours_str, minutes_str, seconds_str = match.groups()

    days = int(days_str) if days_str else 0
    hours = int(hours_str) if hours_str else 0
    minutes = int(minutes_str) if minutes_str else 0
    seconds = int(seconds_str) if seconds_str else 0

    # Check if T was present but no H/M/S followed (e.g., P1DT)
    if "T" in duration_str and not (hours_str or minutes_str or seconds_str):
        # If only T is present after P (PT), it's 0 seconds.
        # If T is present after D (P1DT), it's still valid, just means 0 time component.
        pass  # No warning needed here, the values are correctly 0

    # Check if anything was captured
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
        # Allow PT0S, P0D etc. Check if the original string had *any* numbers
        if not any(char.isdigit() for char in duration_str):
            # Handle P, PT - treat as 0 duration
            if duration_str in ["P", "PT"]:
                return 0
            else:  # Something else weird like PXM or PTD
                print(
                    f"\tWarning: Duration string '{duration_str}' has no valid numeric components."
                )
                return None
        # If it had numbers but they were all zero (like P0D, PT0S), that's valid 0 duration
        # The code below will correctly calculate 0 seconds

    # Calculate total seconds using timedelta
    try:
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        total_seconds = int(delta.total_seconds())
        # Check for negative duration which shouldn't happen with YouTube durations
        if total_seconds < 0:
            print(f"\tWarning: Calculated negative duration for {duration_str}")
            return None
        return total_seconds
    except ValueError as e:
        # This might happen if values are excessively large, though unlikely for video durations
        print(
            f"\tWarning: Error calculating timedelta for duration {duration_str}: {e}"
        )
        return None
