from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from flask_app.models import UserBook, Audiobook, db
from flask_app.modules.mp3_downloader import download_audiobook_mp3
from flask_app.modules.helpers import encode_user_id
import os

user_books = Blueprint("user_books", __name__, url_prefix="/api/user-books")


@user_books.route("", methods=["GET"])
@login_required
def get_user_books():
    """Get all books in the current user's library."""
    books = UserBook.query.filter_by(user_id=current_user.id).order_by(UserBook.created_at.desc()).all()
    return jsonify({
        "books": [book.to_dict() for book in books],
        "total": len(books)
    })


@user_books.route("/<int:audiobook_id>", methods=["POST"])
@login_required
def add_user_book(audiobook_id: int):
    """Add an audiobook to the current user's library and trigger MP3 download."""
    audiobook = Audiobook.query.get_or_404(audiobook_id)

    existing = UserBook.query.filter_by(
        user_id=current_user.id,
        audiobook_id=audiobook_id
    ).first()

    if existing:
        return jsonify({"error": "Book already in your library"}), 400

    # Check if user already has 5 books
    user_books_count = UserBook.query.filter_by(user_id=current_user.id).count()
    if user_books_count >= 5:
        return jsonify({"error": "You have reached the maximum of 5 books. Please delete at least 1 book."}), 400

    user_book = UserBook(
        user_id=current_user.id,
        audiobook_id=audiobook_id,
        status='pending'
    )

    db.session.add(user_book)
    db.session.commit()

    download_audiobook_mp3(user_book.id)

    return jsonify({
        "message": "Book added to your library",
        "book": user_book.to_dict()
    }), 201


@user_books.route("/<int:user_book_id>", methods=["DELETE"])
@login_required
def delete_user_book(user_book_id: int):
    """Delete a book from the current user's library and remove the MP3 file."""
    user_book = UserBook.query.filter_by(
        id=user_book_id,
        user_id=current_user.id
    ).first_or_404()

    if user_book.mp3_file_path and os.path.exists(user_book.mp3_file_path):
        try:
            os.remove(user_book.mp3_file_path)
        except OSError as e:
            print(f"Error deleting MP3 file {user_book.mp3_file_path}: {e}")

    db.session.delete(user_book)
    db.session.commit()

    return jsonify({"message": "Book removed from your library"}), 200


@user_books.route("/check/<int:audiobook_id>", methods=["GET"])
@login_required
def check_user_book(audiobook_id: int):
    """Check if an audiobook is in the current user's library."""
    exists = UserBook.query.filter_by(
        user_id=current_user.id,
        audiobook_id=audiobook_id
    ).first() is not None

    return jsonify({"in_library": exists})


@user_books.route("/rss-url", methods=["GET"])
@login_required
def get_rss_url():
    """Get the RSS feed token for the current user's library."""
    token = encode_user_id(current_user.id)

    return jsonify({"token": token})
