from flask import current_app
from flask.cli import with_appcontext
from flask_app.modules.youtube_crawler import crawl_youtube
from flask_app.models import Category, Author, Audiobook, db
import random
from sqlalchemy import func


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
                # Execute raw SQL to delete from the association table
                db.session.execute(
                    f"DELETE FROM audiobook_categories WHERE audiobook_id = {audiobook_id}"
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
