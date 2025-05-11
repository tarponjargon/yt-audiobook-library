import requests
import os
import click
from rapidfuzz import fuzz, process as fuzz_process


def get_book_info(book_title, author=None):
    """
    Queries the Google Books API to find book details based on the book title.
    (Added better error handling and validation)
    """
    BOOKS_API_URL = os.getenv("BOOKS_API_URL")

    query = f'intitle:"{book_title}"'
    if author:
        query += f' inauthor:"{author}"'
    params = {
        "q": query,  # More specific title search
        "key": os.getenv("GOOGLE_BOOKS_API_KEY"),
        "maxResults": 5,  # Limit results
        "printType": "books",  # Search only for books
    }

    try:
        response = requests.get(BOOKS_API_URL, params=params)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"\tError querying Google Books API for '{book_title}': {e}")
        exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\tHTTP error querying Google Books API for '{book_title}': {e}")
        exit(1)
    except requests.exceptions.Timeout as e:
        print(f"\tTimeout error querying Google Books API for '{book_title}': {e}")
        exit(1)

    data = response.json()
    items = data.get("items")

    if not items:
        return None

    # Extract potential titles and their corresponding items
    candidates = []
    for item in items:
        volume_info = item.get("volumeInfo", {})
        title = volume_info.get("title")
        authors = volume_info.get("authors")
        # Basic filter: require title and authors
        if title and authors:
            candidates.append({"title": title, "item": item})

    if not candidates:
        return None

    # Use fuzzy matching on the candidate titles
    candidate_titles = [c["title"] for c in candidates]
    best_match = fuzz_process.extractOne(
        book_title,
        candidate_titles,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=75,  # Slightly higher cutoff
    )

    if best_match is None:
        return None

    best_match_title, score, _ = best_match

    best_candidate = next(
        (c for c in candidates if c["title"].lower() == best_match_title.lower()),
        None,
    )

    if not best_candidate:
        return None  # Should not happen

    volume_info = best_candidate["item"].get("volumeInfo", {})

    # Ensure essential info is present after matching
    final_title = volume_info.get("title")
    final_authors = volume_info.get("authors", [])
    if not final_title or not final_authors:
        return None

    # Extract thumbnail URL (prefer larger sizes if available, default to 'thumbnail')
    image_links = volume_info.get("imageLinks", {})
    book_thumbnail_url = image_links.get("thumbnail")  # Default to 'thumbnail'

    book_title = final_title
    if volume_info.get("subtitle"):
        book_title += f": {volume_info.get('subtitle')}"

    full_description = volume_info.get("description", "")
    if volume_info.get("categories"):
        full_description += "\n\nCategories: " + ", ".join(
            volume_info.get("categories", [])
        )

    return {
        "title": book_title,
        "author": final_authors[0] if final_authors else None,
        "description": full_description,
        "thumbnail": book_thumbnail_url,
    }
