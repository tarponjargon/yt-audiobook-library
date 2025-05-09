from flask import current_app
from flask.cli import with_appcontext
from flask_app.modules.youtube_crawler import crawl_youtube
from flask_app.models import Category, Author
import random


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
