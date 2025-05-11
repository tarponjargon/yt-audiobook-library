from flask import current_app
from flask.cli import with_appcontext
from flask_app.modules.youtube_crawler import crawl_youtube
from flask_app.models import Category, Author, Audiobook, db, audiobook_categories
import random
from sqlalchemy import func, text
from curl_cffi import requests
import logging


@current_app.cli.command("update_books")
@with_appcontext
def update_books():
    # # Get all categories from the database
    # categories = Category.query.with_entities(Category.name).all()

    # # Loop through each category and crawl YouTube
    # for category in categories:
    #     category_name = category.name
    #     print(f"Crawling YouTube for category: {category_name}")
    #     crawl_youtube(f'intitle:"audiobook" {category_name}')

    # Get all authors from the database
    authors = Author.query.with_entities(Author.name).all()

    # Randomize the authors list
    authors = list(authors)  # Convert SQLAlchemy result to list
    random.shuffle(authors)
    print(f"Randomized {len(authors)} authors for processing")

    # Loop through each category and crawl YouTube
    for author in authors:
        author_name = author.name
        print(f"Crawling YouTube for author: {author_name}")
        crawl_youtube(f'intitle:"audiobook" {author_name}')


@current_app.cli.command("dedupe_books")
@with_appcontext
def dedupe_books():
    """Delete duplicate audiobook records with the same title and author_id."""
    print("Starting deduplication of audiobooks...")
    
    # Find duplicate groups based on title and author_id
    duplicate_groups = db.session.query(
        Audiobook.title,
        Audiobook.author_id,
        func.count().label('count'),
        func.array_agg(Audiobook.id).label('ids')
    ).group_by(
        Audiobook.title,
        Audiobook.author_id
    ).having(
        func.count() > 1
    ).all()
    
    total_duplicates = 0
    total_deleted = 0
    
    # Process each group of duplicates
    for group in duplicate_groups:
        title, author_id, count, ids = group
        total_duplicates += count
        
        # Keep the first record, delete the rest
        ids_to_delete = ids[1:]
        total_deleted += len(ids_to_delete)
        
        print(f"Found {count} duplicates for '{title}' (author_id: {author_id})")
        print(f"  Keeping ID: {ids[0]}, Deleting IDs: {ids_to_delete}")
        
        try:
            # First, delete the associations in the audiobook_categories table
            for audiobook_id in ids_to_delete:
                # Check if the audiobook has any categories before trying to delete associations
                audiobook = Audiobook.query.get(audiobook_id)
                if audiobook and audiobook.categories:
                    # Execute raw SQL to delete from the association table using SQLAlchemy text()
                    db.session.execute(
                        text(f"DELETE FROM audiobook_categories WHERE audiobook_id = {audiobook_id}")
                    )
            
            # Then delete the duplicate audiobook records
            Audiobook.query.filter(Audiobook.id.in_(ids_to_delete)).delete(synchronize_session=False)
            
            # Commit after each group to avoid large transactions
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error processing group with title '{title}': {str(e)}")
    
    print(f"Deduplication complete. Found {len(duplicate_groups)} duplicate groups with {total_duplicates} total records.")
    print(f"Kept {len(duplicate_groups)} records and deleted {total_deleted} duplicates.")


@current_app.cli.command("prune_books")
@with_appcontext
def prune_books():
    """
    Delete audiobook records where the thumbnail URL returns a 404 error.
    This indicates the YouTube video has been removed or made private.
    """
    print("Starting pruning of unavailable audiobooks...")
    
    # Get all audiobooks
    audiobooks = Audiobook.query.all()
    total_count = len(audiobooks)
    deleted_count = 0
    error_count = 0
    skipped_count = 0
    available_count = 0
    
    print(f"Found {total_count} audiobooks to check")
    
    # Set up curl_cffi with Chrome browser impersonation
    session = requests.Session()
    
    # Process each audiobook
    for i, audiobook in enumerate(audiobooks):
        if i % 10 == 0:
            print(f"Checking audiobook {i+1}/{total_count}...")
        
        # Skip if no thumbnail URL
        if not audiobook.thumbnail:
            print(f"Skipping audiobook ID {audiobook.id}: No thumbnail URL")
            skipped_count += 1
            continue
        
        try:
            # Make a HEAD request to check if the thumbnail exists
            response = session.head(
                audiobook.thumbnail,
                impersonate="chrome",  # Impersonate Chrome browser
                timeout=10,            # 10 second timeout
                allow_redirects=True   # Follow redirects
            )
            
            # If the response is 404 (Not Found) or 403 (Forbidden), the video is likely gone
            if response.status_code in [404, 403]:
                print(f"Audiobook ID {audiobook.id} ({audiobook.title}) is unavailable (Status: {response.status_code})")
                
                try:
                    # First, get all related data for logging purposes
                    author_name = audiobook.author.name if audiobook.author else "No author"
                    category_names = [cat.name for cat in audiobook.categories]
                    
                    # Check if there are any category associations before trying to delete them
                    if audiobook.categories:
                        # Delete from the association table first using SQLAlchemy text()
                        db.session.execute(
                            text(f"DELETE FROM audiobook_categories WHERE audiobook_id = {audiobook.id}")
                        )
                    
                    # Delete the audiobook record
                    db.session.delete(audiobook)
                    db.session.commit()
                    deleted_count += 1
                    print(f"  Deleted audiobook ID {audiobook.id} - Author: {author_name}, Categories: {category_names}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"  Error deleting audiobook ID {audiobook.id}: {str(e)}")
                    error_count += 1
            else:
                # Audiobook is available
                available_count += 1
                if i % 50 == 0:  # Only log every 50th available book to reduce output
                    print(f"Audiobook ID {audiobook.id} is available (Status: {response.status_code})")
        
        except Exception as e:
            print(f"Error checking audiobook ID {audiobook.id}: {str(e)}")
            error_count += 1
    
    print("\nPruning complete. Summary:")
    print(f"Total audiobooks checked: {total_count}")
    print(f"Available audiobooks: {available_count}")
    print(f"Unavailable audiobooks deleted: {deleted_count}")
    print(f"Audiobooks skipped (no thumbnail): {skipped_count}")
    print(f"Errors encountered: {error_count}")
