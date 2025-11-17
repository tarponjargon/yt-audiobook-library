import os
import threading
from datetime import datetime
from typing import Optional
import re


def sanitize_filename(text: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized filename-safe string
    """
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '_', text)
    text = text.strip('._')
    return text[:100]


def download_audiobook_mp3(user_book_id: int) -> None:
    """
    Start a background thread to download and convert a YouTube video to MP3.

    Args:
        user_book_id: ID of the UserBook record to process
    """
    print(f"[MP3 Download] Starting background thread for UserBook {user_book_id}")
    thread = threading.Thread(target=_download_worker, args=(user_book_id,), daemon=True)
    thread.start()
    print(f"[MP3 Download] Background thread started with thread ID: {thread.ident}")


def _download_worker(user_book_id: int) -> None:
    """
    Background worker that downloads a YouTube video and converts it to MP3.

    Args:
        user_book_id: ID of the UserBook record to process
    """
    from flask_app import create_app
    from flask_app.models import UserBook, db

    print(f"[MP3 Download] Worker started for UserBook {user_book_id}")

    app = create_app()
    with app.app_context():
        user_book = UserBook.query.get(user_book_id)
        if not user_book:
            print(f"[MP3 Download] ERROR: UserBook {user_book_id} not found")
            return

        try:
            print(f"[MP3 Download] Setting status to 'downloading' for UserBook {user_book_id}")
            user_book.status = 'downloading'
            db.session.commit()

            audiobook = user_book.audiobook
            video_id = audiobook.video_id
            title = sanitize_filename(audiobook.title)
            author = sanitize_filename(audiobook.author.name if audiobook.author else "Unknown")

            print(f"[MP3 Download] Processing: {audiobook.title} by {audiobook.author.name if audiobook.author else 'Unknown'}")
            print(f"[MP3 Download] Video ID: {video_id}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{title}_{author}.mp3"

            output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'audiobooks')
            os.makedirs(output_dir, exist_ok=True)
            print(f"[MP3 Download] Output directory: {output_dir}")

            output_path = os.path.join(output_dir, filename)
            print(f"[MP3 Download] Target filename: {filename}")

            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"[MP3 Download] YouTube URL: {youtube_url}")

            import subprocess
            print(f"[MP3 Download] Starting yt-dlp download...")

            # Prepare metadata for MP3 tags
            metadata_title = audiobook.title
            metadata_artist = audiobook.author.name if audiobook.author else "Unknown Author"

            result = subprocess.run([
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '--audio-quality', '128K',
                '--embed-metadata',
                '--parse-metadata', f'title:{metadata_title}',
                '--parse-metadata', f'artist:{metadata_artist}',
                '--progress',
                '--newline',
                '--ffmpeg-location', '/usr/bin/ffmpeg',
                '-o', output_path.replace('.mp3', '.%(ext)s'),
                youtube_url
            ], capture_output=False, text=True, timeout=3600)

            print(f"[MP3 Download] yt-dlp exit code: {result.returncode}")
            if result.stdout:
                print(f"[MP3 Download] yt-dlp stdout: {result.stdout[:500]}")
            if result.stderr:
                print(f"[MP3 Download] yt-dlp stderr: {result.stderr[:500]}")

            if result.returncode != 0:
                raise Exception(f"yt-dlp failed with code {result.returncode}: {result.stderr}")

            print(f"[MP3 Download] Download completed successfully")
            user_book.status = 'completed'
            user_book.mp3_file_path = output_path
            db.session.commit()

            print(f"[MP3 Download] SUCCESS: MP3 saved to {output_path}")

        except Exception as e:
            print(f"[MP3 Download] ERROR: Failed to download MP3 for UserBook {user_book_id}: {e}")
            import traceback
            print(f"[MP3 Download] Traceback: {traceback.format_exc()}")
            user_book.status = 'failed'
            db.session.commit()
