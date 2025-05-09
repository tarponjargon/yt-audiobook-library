import os
from flask_app.modules.extensions import db
from flask_app.models import Audiobook, SkippedVideo
from flask_app.modules.llm.schema import Book, Author, BookLanguage, BookCategories
from flask_app.modules.llm.chat_client import ollama_request


def guess_book_name(video_title):
    """
    Attempts to get book name with llm
    """
    book_name = None
    try:
        prompt = f"""
          This string contains a book title and may contain author, as well as other text.
          Give me the book title and author (if available). If no author is available, return an empty string for author.
          Here is the book title: {video_title}
        """
        book_name = ollama_request(prompt, None, Book)
        # print(f"\tOllama response: {book_name}")
    except Exception as e:
        print(f"\tError querying Ollama for book details: {e}")
    return book_name


def guess_book_author(text):
    """
    Attempts to get book author with llm
    """
    data = {}
    try:
        prompt = f"""
          This string contains a book title, description and may contain author name, as well as other text.
          Try to determine the author name. If no author is available, return an empty string for author.
          Here is the text: {text}
        """
        data = ollama_request(prompt, None, Author)
    except Exception as e:
        print(f"\tError querying Ollama for book details: {e}")
    author = data.get("author", None)
    return author if author and author.lower() != "unknown" else None


def guess_book_language(text):
    """
    Attempts to check if the autobook is in English
    """
    data = {}
    try:
        prompt = f"""
          Tell me if this text is in English or not. If it is, return true, otherwise return false.
          Here is the text: {text}
        """
        data = ollama_request(prompt, None, BookLanguage)
    except Exception as e:
        print(f"\tError querying Ollama for book language: {e}")
    return data.get("is_english", None)


def guess_book_categories(text):
    """
    Attempts to get book categorization with llm
    """
    data = {}
    valid_categories = os.getenv("BOOK_CATEGORIES")
    valid_categories_list = valid_categories.split(",")
    try:
        prompt = f"""
          This string contains text describing an audiobook.
          Based on text, classify the book in one or more of
          the following categories: {valid_categories}.
          Do not include any categories outside of this list.
          Here is the book text: {text}
        """
        data = ollama_request(prompt, None, BookCategories)
    except Exception as e:
        print(f"\tError querying Ollama for book details: {e}")
    categories = data.get("categories", [])
    # Filter categories to only include valid ones
    categories = [
        category for category in categories if category in valid_categories_list
    ]
    return categories
