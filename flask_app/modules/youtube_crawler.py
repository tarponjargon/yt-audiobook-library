import random
import re
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from flask_app.modules.user_agent_generator import ValidUAGenerator
from flask_app.modules.book import (
    check_if_book_exists,
    store_book_info,
    process_book_name,
    ineligible_video,
)
from flask_app.modules.llm.book import (
    guess_book_name,
    guess_book_author,
    guess_book_language,
    guess_book_categories,
)
from flask_app.modules.helpers import string_to_ascii
from flask_app.modules.google_books import get_book_info
from flask_app.modules.extensions import db
import json


def get_element_text(video_result, selector):
    """
    Get the text content of a DOM element using Playwright.
    """
    pr_text = ""
    pr_element = video_result.query_selector(selector)
    if pr_element:
        pr_text = pr_element.inner_text()
    return pr_text.strip()


def get_element_attribute(video_result, selector, attribute):
    """
    Get the attribute value of a DOM element using Playwright.
    """
    pr_element = video_result.query_selector(selector)
    if pr_element:
        return pr_element.get_attribute(attribute)

    return None


def parse_video_id(video_result):
    """
    Get the video ID from a DOM element using Playwright.
    Returns the YouTube video ID from the href attribute.
    """
    pr_element = video_result.query_selector("a#thumbnail")
    if pr_element:
        href = pr_element.get_attribute("href")
        if href:
            # Extract the video ID from the URL
            # YouTube URLs are in the format /watch?v=VIDEO_ID or /watch?v=VIDEO_ID&...
            match = re.search(r"watch\?v=([^&]+)", href)
            if match:
                return match.group(1)  # Return the captured video ID

    return None


def convert_duration_to_seconds(duration_str):
    """
    Convert a YouTube duration string (HH:MM:SS, MM:SS, or SS) to seconds.
    """
    # Handle empty or invalid input
    if not duration_str or not isinstance(duration_str, str):
        return 0

    # Remove any non-digit or non-colon characters
    duration_str = re.sub(r"[^\d:]", "", duration_str)

    # Split by colon
    parts = duration_str.split(":")

    # Convert based on format (HH:MM:SS, MM:SS, or SS)
    if len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 1 and parts[0].isdigit():  # SS
        return int(parts[0])
    else:
        return 0  # Invalid format


def process_video_elements(video_elements):
    # Loop through each video element and print it

    for i, video in enumerate(video_elements):
        print(f"Video #{i+1}:")
        # Print the element (this will show a representation of the Playwright element)
        # print(video)

        video_id = parse_video_id(video)
        if not video_id:
            print("No video ID found")
            # # Take a screenshot of the problematic element for debugging
            # screenshot_path = f"tmp/no_video_id_{i}.png"
            # os.makedirs("tmp", exist_ok=True)
            # try:
            #     video.screenshot(path=screenshot_path)
            #     print(f"Screenshot saved to {screenshot_path}")
            # except Exception as e:
            #     print(f"Failed to take screenshot: {e}")
            # print(video)
            continue
        book = {
            "video_id": video_id,
            "title": process_book_name(get_element_text(video, "h3")),
            "description": get_element_text(video, ".metadata-snippet-text"),
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "author": None,
            "categories": [],
            "duration": convert_duration_to_seconds(
                get_element_text(video, "[id='time-status']")
            ),
        }

        # Print the book dictionary as readable JSON
        print(f"Book: {json.dumps(book, indent=2)}")

        if not __name__ == "__main__":  # only do this if we're running in flask
            process_book_data(book)
        print("-------------------")


def process_book_data(book):
    # Check if the book already exists in the database
    if check_if_book_exists(book["video_id"]):
        print(f"Video ID {book["video_id"]} already exists in the database.")
        return False

    # check if the video is too short to be an audiobook
    if book["duration"] < int(os.getenv("MIN_BOOK_DURATION", 0)):
        ineligible_video(book["video_id"], "Too short")
        return False

    # check that this video is in english
    book_info = {}
    language_context = string_to_ascii(book["title"]) + string_to_ascii(
        book["description"]
    )
    is_english = guess_book_language(language_context)
    if not is_english:
        ineligible_video(book["video_id"], "Not in English (det. by LLM)")
        return False

    # use an LLM to try to determine if the book title and description are in English
    # if not, skip the video
    book_info = {}
    language_context = string_to_ascii(book["title"]) + string_to_ascii(
        book["description"]
    )
    is_english = guess_book_language(language_context)
    if not is_english:
        ineligible_video(book["video_id"], "Not in English (det. by LLM)")
        return False

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
        return False

    # guess categories from the description
    categories_context = book["title"] + string_to_ascii(book["description"])
    book["categories"] = guess_book_categories(categories_context)

    print(f"Book: {json.dumps(book, indent=2)}")

    # Store the processed book data
    return store_book_info(book)


def simulate_user_interaction(page):
    # Simulate user interaction by moving the mouse and arrow keys
    start = random.randint(1, 800)
    end = random.randint(1, 800)
    page.mouse.move(start, end)
    # if start is even, move mouse down, else move mouse up
    if start % 2 == 0:
        page.mouse.move(start, end + 100)
    else:
        page.mouse.move(start, end - 100)
    keyList = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]
    key = random.choice(keyList)
    page.keyboard.press(key)


def crawl_youtube(query, max_scrolls=30):
    with sync_playwright() as p:
        # Launch browser

        headless = False if __name__ == "__main__" else True

        browser = p.chromium.launch(headless=headless)  # Set headless=True for no UI

        # Create a new page with specific viewport size
        generator = ValidUAGenerator()
        ua = generator.generate()
        context = browser.new_context(
            viewport={"width": 1280, "height": 800}, user_agent=ua
        )
        page = context.new_page()
        stealth_sync(page)

        # Construct the search URL
        term = query.replace(" ", "+")
        search_url = f"https://www.youtube.com/results?search_query={term}"

        # Navigate to the search results page
        page.goto(search_url)

        # Additionally wait for search results to be visible
        try:
            page.wait_for_selector("ytd-video-renderer")
        except Exception as e:
            print(f"Error waiting for search results: {e}")
            # Take a screenshot to see what's happening
            screenshot_path = "tmp/error_screenshot.png"
            os.makedirs("tmp", exist_ok=True)
            try:
                page.screenshot(path=screenshot_path)
                print(f"Error screenshot saved to {screenshot_path}")
            except Exception as screenshot_error:
                print(f"Failed to take error screenshot: {screenshot_error}")
            browser.close()
            return

        print("Search results loaded successfully!")

        # Simulate user interaction (optional)
        simulate_user_interaction(page)

        # Get initial videos and process them
        processed_ids = set()
        load_and_process_new_videos(page, processed_ids)

        # Continue scrolling and processing new videos
        print("Scrolling to load more videos...")
        scroll_and_process_new_videos(page, processed_ids, max_scrolls)

        # Close the browser
        browser.close()


def load_and_process_new_videos(page, processed_ids):
    # Get all current video elements
    video_elements = page.query_selector_all("ytd-video-renderer")

    # Filter out only new elements that haven't been processed yet
    new_videos = []
    for video in video_elements:
        # Get a unique identifier for the element
        video_id = page.evaluate(
            "(element) => element.getAttribute('data-video-id')", video
        )
        if not video_id:
            # Fallback to using inner HTML hash if data-video-id is not available
            title_elem = video.query_selector("h3")
            if title_elem:
                title = title_elem.inner_text()
                video_id = title  # Use title as ID

        # If we haven't processed this video yet, add it to the list
        if video_id and video_id not in processed_ids:
            new_videos.append(video)
            processed_ids.add(video_id)

    # Process only the new videos
    print(f"Found {len(new_videos)} new video elements.")
    process_video_elements(new_videos)
    return len(new_videos)


def scroll_and_process_new_videos(page, processed_ids, max_scrolls=30):
    """Scroll down and process new videos that appear, limited by max_scrolls"""

    for scroll_count in range(max_scrolls):
        # Scroll down to trigger loading more videos
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")

        # wait random time between 1.5 and 4 seconds
        page.wait_for_timeout(random.randint(1500, 4000))

        # Find and process any new videos
        new_count = load_and_process_new_videos(page, processed_ids)

        print(f"Scroll #{scroll_count + 1}: Processed {new_count} new videos")

        # If no new videos were found, we might have reached the end
        if new_count == 0:
            print(
                "No new videos found. May have reached the end or need to wait longer."
            )
            # Try one more time with a longer wait
            page.wait_for_timeout(random.randint(3000, 5500))
            new_count = load_and_process_new_videos(page, processed_ids)
            if new_count == 0:
                print("Still no new videos. Stopping scrolling.")
                break


if __name__ == "__main__":
    # Example usage
    query = "audiobook"
    crawl_youtube(query)
