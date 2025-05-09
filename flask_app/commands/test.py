import click
from flask import current_app
from flask.cli import with_appcontext
import os
import requests
import time
import json
from rapidfuzz import fuzz, process as fuzz_process
from flask_app.modules.books import (
    process_book_name,
    string_to_ascii,
    parse_iso8601_duration,
)
from flask_app.modules.extensions import db
from flask_app.models import Audiobook, Category, SkippedVideo, YoutubeSearchState
from flask_app.modules.llm import ollama_request
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone


@current_app.cli.command("update_books")
@with_appcontext
def update_books():
    """Search YouTube, coalesce title/author/desc against Google Books and an LLM, and store in DB using SQLAlchemy."""

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    YOUTUBE_SEARCH_API_URL = os.getenv("YOUTUBE_SEARCH_API_URL")
    MAX_PAGES = 200  # Limit the number of pages to fetch

    search_params = {
        "part": "snippet",
        "q": "audiobook",
        "key": GOOGLE_API_KEY,
        "maxResults": 50,
        "type": "video",
        "videoDuration": "long",
    }

    books_added_count = 0
    page_count = 0

    # --- Resume Logic ---
    next_page_token = get_saved_page_token()
    if next_page_token:
        print(f"Resuming search from saved page token: {next_page_token[:10]}...")
    else:
        print("Starting search from the beginning.")
    # --- End Resume Logic ---

    while page_count < MAX_PAGES:
        page_count += 1
        print(f"\nFetching page {page_count} of YouTube search results...")

        if next_page_token:
            search_params["pageToken"] = next_page_token

        try:
            response = requests.get(
                YOUTUBE_SEARCH_API_URL, params=search_params, timeout=15
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(
                f"Error fetching search data from YouTube API on page {page_count}: {e}"
            )
            break  # Stop processing if a page fails

        data = response.json()
        current_page_token = next_page_token  # Store token used for this page fetch
        next_page_token = data.get("nextPageToken")

        # --- Save State ---
        if next_page_token:
            save_page_token(next_page_token)
        # --- End Save State ---

        print(
            f"Processing {len(data.get('items', []))} items from page {page_count}..."
        )

        for vid in data.get("items", []):

            video_id = vid["id"].get("videoId")

            # skip if we've already processed it
            if check_if_book_exists(video_id):
                print(f"\nSkipped: Book '{video_id}' already processed")
                continue

            item = get_full_video_details(video_id)

            # print(f"\nProcessing item: {item}")
            book = {
                "video_id": video_id,
                "title": process_book_name(item["snippet"]["title"]),
                "description": item["snippet"]["description"],
                # Use snippet tags as potential initial categories, will be refined later
                "categories": item["snippet"].get("tags", []),
                "thumbnail": item["snippet"].get("thumbnails").get("high").get("url"),
                "author": None,
                # 'categories' list will be populated by guess_book_categories later
                "duration": 0,
            }

            print(f"\nProcessing video: {book['title']} (ID: {book['video_id']})")

            # (first) check if the video is in English
            if not check_language(item["snippet"]):
                ineligible_video(book["video_id"], "Not in English")
                continue

            # get duration and skip if it's too short
            book["duration"] = get_video_duration(book["video_id"])
            if book["duration"]:
                # print(f"\tParsed duration: {video_duration} seconds")
                if book["duration"] < int(os.getenv("MIN_BOOK_DURATION", 0)):
                    ineligible_video(book["video_id"], "Too short")
                    continue

            # use an LLM to try to determine if the book title and description are in English
            # if not, skip the video
            book_info = {}
            language_context = string_to_ascii(book["title"]) + string_to_ascii(
                book["description"]
            )
            is_english = guess_book_language(language_context)
            if not is_english:
                ineligible_video(book["video_id"], "Not in English (det. by LLM)")
                continue

            # use an LLM to try to parse out a book title and author from the other
            # gobbledygook people add to the video title
            book_info = {}
            guessed_book_details = guess_book_name(book["title"])
            if guessed_book_details:
                book["author"] = guessed_book_details.get("author")
                book["title"] = guessed_book_details.get("title")

            # if author is not available, try to guess it from the description
            if not book["author"] or book["author"].lower() == "unknown":
                author_context = string_to_ascii(book["description"])
                book["author"] = guess_book_author(author_context)

            # try the google books api to get standardized book info
            # if book info is returned, prefer it over anything we have so far
            book_info = get_book_info(book["title"], book["author"])
            if book_info:
                book["author"] = book_info.get("author")
                book["title"] = book_info.get("title")
                book["description"] = book_info.get("description")
                if not book["thumbnail"]:
                    book["thumbnail"] = book_info["thumbnail"]

            # if no author is available at this point it's likely a garbage book, skip to next
            if not book["author"] or book["author"].lower() == "unknown":
                ineligible_video(book["video_id"], "No author found")
                continue

            # guess categories from the description
            categories_context = book["title"] + string_to_ascii(book["description"])
            book["categories"] = guess_book_categories(categories_context)

            # Format the book dictionary as JSON for readability
            # formatted_book_json = json.dumps(book, indent=4, ensure_ascii=False)
            # print(f"\tFormatted Book JSON:\n{formatted_book_json}")

            # Store the processed book data
            if store_book_info(book):
                books_added_count += 1

            # Store the processed book data
            if store_book_info(book):
                books_added_count += 1

        # if not next_page_token:
        #     print("\nNo more pages to fetch. Clearing saved token.")
        #     clear_page_token() # Clear token on successful completion
        #     break  # Exit the loop if there's no next page token

    if page_count >= MAX_PAGES:
        print(f"\nReached maximum page limit ({MAX_PAGES}). Clearing saved token.")
        clear_page_token()  # Clear token if max pages reached

    print(f"\nFinished processing. Added {books_added_count} new books in total.")


# --- Helper functions for managing page token state ---


def get_saved_page_token():
    """Retrieves the saved YouTube search page token from the database."""
    try:
        state = db.session.execute(
            db.select(YoutubeSearchState).filter_by(key="next_page_token")
        ).scalar_one_or_none()
        return state.value if state else None
    except SQLAlchemyError as e:
        print(f"Database error retrieving page token: {e}", err=True)
        return None


def save_page_token(token):
    """Saves or updates the YouTube search page token in the database."""
    try:
        state = db.session.execute(
            db.select(YoutubeSearchState).filter_by(key="next_page_token")
        ).scalar_one_or_none()
        if state:
            state.value = token
            state.timestamp = datetime.now(timezone.utc)  # Explicitly update timestamp
        else:
            state = YoutubeSearchState(key="next_page_token", value=token)
            db.session.add(state)
        db.session.commit()
        # print(f"\tSaved page token: {token[:10]}...") # Optional: for debugging
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error saving page token: {e}", err=True)


def clear_page_token():
    """Clears the saved YouTube search page token from the database."""
    try:
        state = db.session.execute(
            db.select(YoutubeSearchState).filter_by(key="next_page_token")
        ).scalar_one_or_none()
        if state:
            state.value = None  # Set value to None instead of deleting row
            state.timestamp = datetime.now(timezone.utc)  # Update timestamp
            db.session.commit()
            # print("\tCleared saved page token.") # Optional: for debugging
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error clearing page token: {e}", err=True)


def check_language(snippet):
    """
    Checks if the video is in English
    """
    vid_lang = snippet.get("defaultAudioLanguage")
    if not vid_lang:
        vid_lang = snippet.get("defaultLanguage")

    if not vid_lang:
        return True

    if not vid_lang.lower().startswith("en"):
        return False
    return True


def get_full_video_details(video_id):
    """
    Fetches detailed information about a YouTube video using the YouTube API.
    """
    video_details_params = {
        "part": "snippet,contentDetails",
        "id": video_id,
        "key": os.getenv("GOOGLE_API_KEY"),
    }
    YOUTUBE_VIDEO_API_URL = os.getenv("YOUTUBE_VIDEO_API_URL")
    video_response = requests.get(
        YOUTUBE_VIDEO_API_URL, params=video_details_params, timeout=15
    )
    video_response.raise_for_status()
    data = video_response.json()

    return data.get("items", [{}])[0]


def get_video_duration(video_id):
    video_duration_iso = None
    parsed_duration_seconds = None
    try:
        video_details_params = {
            "part": "contentDetails",
            "id": video_id,
            "key": os.getenv("GOOGLE_API_KEY"),
        }
        YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"
        video_response = requests.get(
            YOUTUBE_VIDEOS_API_URL, params=video_details_params, timeout=15
        )
        video_response.raise_for_status()
        video_data = video_response.json()
        if video_data.get("items"):
            content_details = video_data["items"][0].get("contentDetails")
            if content_details:
                video_duration_iso = content_details.get(
                    "duration"
                )  # This is ISO 8601 format (e.g., "PT1H23M45S")
                if video_duration_iso:
                    parsed_duration_seconds = parse_iso8601_duration(video_duration_iso)

    except requests.exceptions.RequestException as e:
        print(f"\tWarning: Error fetching duration for {video_id}: {e}")

    return parsed_duration_seconds
