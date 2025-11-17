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

# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.

## Core Development Rules

1. Code Quality

   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 120 chars maximum

2. Testing Requirements

   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

3. Code Style

   - PEP 8 naming (snake_case for functions/variables)
   - Class names in PascalCase
   - Constants in UPPER_SNAKE_CASE
   - Document with docstrings
   - Use f-strings for formatting

4. Code quality

   - You will follow the style of existing code
   - Choose to write code of better quality
   - Location of Python `import` statement should always be at the top of the file
     - Unless there is an issue with circular dependency
   - New Python functions should have signatures, even if signatures are missing for existing functions

5. Language

   - When writing documentation like README.md, use simple, plain, direct language and avoid corporate "braggy" or marketing words like "features" and "achievements" and "reliability" and "key".
   - do not use utf8 icons

6. Where to Put Tests and Exploratory Scripts

- Exploration/test scripts → tests/exploration/
- Test data (JSON) → tests/data/
- Unit tests → tests/ (root of tests)

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint
- **No Fallbacks**: Minimize try/except and never write fallbacks.

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organzation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

## Code Formatting

1. Ruff
   - Critical issues:
     - Line length (120 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

## Error Resolution

1. CI Failures

   - Fix order:
     1. Formatting
     2. Type errors
     3. Linting
   - Type errors:
     - Get full line context
     - Check Optional types
     - Add type narrowing
     - Verify function signatures

2. Common Issues

   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

3. Best Practices
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly

\
