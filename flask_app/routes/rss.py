from flask import Blueprint, Response, request, url_for
from feedgen.feed import FeedGenerator
from flask_app.models import UserBook, User
from flask_app.modules.helpers import decode_user_id
import os

rss = Blueprint("rss", __name__)

# Public base URL for RSS feed links
PUBLIC_BASE_URL = "https://ytbooks.clipcast.it"


@rss.route("/rss-feed/<token>", methods=["GET"])
def serve_rss_feed(token: str):
    """
    Serve an RSS podcast feed for a user's My Books library.

    Args:
        token: URL-safe encoded user ID token

    Returns:
        RSS XML feed or error response
    """
    user_id = decode_user_id(token)

    if user_id is None:
        return Response("Invalid feed URL", status=400)

    user = User.query.get(user_id)
    if not user:
        return Response("User not found", status=404)

    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.id(f"{PUBLIC_BASE_URL}/rss-feed/{token}")
    fg.title(f"{user.email}'s Audiobook Library")
    fg.link(href=PUBLIC_BASE_URL, rel="alternate")
    fg.description("Your personal audiobook collection from YT-Audiobooks")
    fg.language("en")
    fg.copyright("All rights reserved")

    fg.podcast.itunes_author("YT-Audiobooks")
    fg.podcast.itunes_block(False)
    fg.podcast.itunes_explicit("no")
    fg.podcast.itunes_category("Arts", "Books")

    books = UserBook.query.filter_by(
        user_id=user_id,
        status='completed'
    ).order_by(UserBook.created_at.desc()).all()

    for book in books:
        if not book.mp3_file_path or not os.path.exists(book.mp3_file_path):
            continue

        audiobook = book.audiobook
        if not audiobook:
            continue

        filename = os.path.basename(book.mp3_file_path)
        mp3_url = f"{PUBLIC_BASE_URL}/static/audiobooks/{filename}"

        file_size = 0
        try:
            file_size = os.path.getsize(book.mp3_file_path)
        except OSError:
            pass

        fe = fg.add_entry()
        fe.id(mp3_url)
        fe.title(audiobook.title)
        fe.description(audiobook.description or f"Audiobook: {audiobook.title}")
        fe.link(href=mp3_url)
        fe.pubDate(book.created_at)

        fe.enclosure(mp3_url, str(file_size), "audio/mpeg")

        fe.podcast.itunes_author(audiobook.author.name if audiobook.author else "Unknown Author")
        fe.podcast.itunes_block(False)
        fe.podcast.itunes_explicit("no")

        if audiobook.duration:
            hours = audiobook.duration // 3600
            minutes = (audiobook.duration % 3600) // 60
            seconds = audiobook.duration % 60
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            fe.podcast.itunes_duration(duration_str)

        if audiobook.thumbnail:
            try:
                fe.podcast.itunes_image(audiobook.thumbnail)
            except Exception:
                pass

    rss_feed_data = fg.rss_str(pretty=True).decode("utf-8")

    return Response(rss_feed_data, mimetype="application/rss+xml")
