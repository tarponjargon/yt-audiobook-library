# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube audiobook library application consisting of:
- **Backend**: Flask application that scrapes YouTube for audiobooks, enriches metadata using Google Books API and LLM, and stores in PostgreSQL
- **Frontend**: React/Vite application with TailwindCSS for browsing and searching the audiobook library

## Development Environment

### Running the Application

```bash
# Start all services (Flask backend, React frontend, PostgreSQL, Adminer)
docker-compose up

# Access points:
# - Frontend: http://localhost:3001
# - Backend API: http://localhost:5001
# - Adminer (DB GUI): http://localhost:8081
```

### Working with the Flask Backend

```bash
# Enter the Flask container
docker-compose exec flask-app bash

# Run Flask commands (inside container)
flask <command>

# Flask interactive shell with autoreload
flask shell
ctx = app.test_request_context()
ctx.push()
load_ext autoreload
autoreload 2
```

### Working with the Frontend

```bash
# Enter the frontend container
docker-compose exec frontend sh

# Development server (already running via docker-compose)
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Common Flask Commands

### Audiobook Management

```bash
# Full pipeline: scrape by author, by category, general, dedupe, and prune
flask add_books_full

# Add audiobooks by author (crawls all authors in DB)
flask add_books_by_author

# Add audiobooks by category (crawls all categories in DB)
flask add_books_by_category

# Add audiobooks with general search
flask add_books

# Add audiobooks for a specific author
flask add_author "Author Name"

# Remove duplicate audiobooks (same title + author)
flask dedupe_books

# Remove audiobooks whose thumbnails return 404 (deleted videos)
flask prune_books

# Set default sort order for categories
flask set_category_sort_order
```

### Database Management

```bash
# Initialize migrations (if not already done)
flask db init

# Create a new migration after model changes
flask db migrate -m "description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Architecture

### Backend Structure

```
flask_app/
├── __init__.py          # App factory, extension registration, blueprint registration
├── models.py            # SQLAlchemy models (Audiobook, Author, Category, User, etc.)
├── commands/            # Flask CLI commands
│   ├── books.py         # Audiobook management commands
│   └── test.py          # Test commands
├── routes/              # Blueprint route handlers
│   ├── api.py           # Main API endpoints (search, categories, audiobooks)
│   ├── auth.py          # Authentication endpoints
│   ├── favorites.py     # User favorites endpoints
│   └── views.py         # Template views (if any)
├── modules/             # Core business logic
│   ├── youtube_crawler.py    # Playwright-based YouTube scraping
│   ├── book.py               # Book processing and storage logic
│   ├── google_books.py       # Google Books API integration
│   ├── helpers.py            # Utility functions
│   ├── extensions.py         # Flask extension instances (db, login_manager, bcrypt)
│   └── llm/                  # LLM integration for metadata enrichment
│       ├── book.py           # Book-specific LLM functions (title, author, language, categories)
│       ├── chat_client.py    # LLM client interface
│       └── schema.py         # LLM response schemas
└── config/              # Configuration files
```

### Frontend Structure

```
frontend/src/
├── App.jsx              # Main app with routing
├── main.jsx             # Entry point
├── pages/               # Page components
│   ├── HomePage.jsx              # Browse categories and recent audiobooks
│   ├── CategoryPage.jsx          # Audiobooks in a category
│   ├── AudiobookDetailPage.jsx   # Individual audiobook details
│   ├── SearchResultsPage.jsx     # Search results
│   ├── LoginPage.jsx             # User login
│   ├── RegisterPage.jsx          # User registration
│   └── FavoritesPage.jsx         # User's favorite audiobooks
├── components/          # Reusable components
├── context/             # React context providers (AuthContext)
├── store/               # Zustand state management
└── api/                 # API client functions
```

### Database Models

**Core Entities:**
- `Audiobook`: YouTube video data enriched with metadata (title, author, categories, thumbnail, duration)
- `Author`: Audiobook authors (many-to-one with Audiobook)
- `Category`: Audiobook categories (many-to-many with Audiobook via `audiobook_categories`)
- `User`: Application users with authentication
- `user_favorites`: Many-to-many association between Users and Audiobooks

**Supporting Tables:**
- `SkippedVideo`: Videos skipped during processing (with reason)
- `YoutubeSearchState`: Stores pagination tokens for YouTube searches

### Key Processing Flow

1. **YouTube Crawling** (`youtube_crawler.py`):
   - Uses Playwright with stealth mode to search YouTube
   - Parses video title, thumbnail, duration, video ID
   - Checks if video already exists or was previously skipped

2. **Metadata Enrichment** (`modules/llm/book.py` and `google_books.py`):
   - LLM guesses book title, author, language, and categories from YouTube metadata
   - Google Books API called to enrich with additional data
   - Results stored in database with relationships

3. **API Layer** (`routes/api.py`):
   - RESTful endpoints for searching, browsing by category, fetching audiobook details
   - Pagination support
   - User authentication and favorites management

## Environment Variables

Required in `.env`:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL connection
- `SECRET_KEY`: Flask secret key
- `GOOGLE_BOOKS_API_KEY`: Google Books API access
- LLM provider configuration (varies by provider: OpenAI, Anthropic, Ollama, etc.)

## Testing and Database

### Database Inspection

```bash
# Check for duplicates
SELECT title, author_id, COUNT(*) AS num_occurrences
FROM audiobooks
GROUP BY title, author_id
HAVING COUNT(*) > 1

# Access Adminer at http://localhost:8081
# Use credentials from .env file
```

### Data Initialization

Initial data dump available at `init_data/ytbooks_dump.sql` and loaded automatically via `init_data/init.sh` on first PostgreSQL container startup.

## Important Notes

- YouTube crawling uses Playwright with browser impersonation to avoid blocking
- LLM is used to intelligently parse book metadata from unstructured YouTube titles/descriptions
- The application handles deleted YouTube videos via the `prune_books` command
- Deduplication is title+author based, keeping the first record found
- Flask uses SQLAlchemy with lazy loading optimization and logging disabled for better performance
