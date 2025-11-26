# YT Audiobook Library

A web application that scrapes YouTube for audiobooks, enriches metadata using Google Books API and LLMs, and provides a browseable library with personal podcast feed support.

## What It Does

- Crawls YouTube for audiobook content using Playwright
- Enriches video metadata with Google Books API and LLM-based title/author extraction
- Stores audiobooks in PostgreSQL with categories, authors, ratings, and thumbnails
- Provides a React frontend for browsing, searching, and rating audiobooks
- Allows users to add books to their personal library ("My Books")
- Downloads audiobooks as MP3 files using yt-dlp
- Generates RSS podcast feeds so users can listen in their preferred podcast app

## Application Stack

- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: React with Vite, TailwindCSS
- **Database**: PostgreSQL 15
- **Containerization**: Docker and Docker Compose
- **YouTube Scraping**: Playwright with stealth mode
- **MP3 Conversion**: yt-dlp with ffmpeg
- **RSS Feeds**: feedgen library
- **HTTPS Tunnel**: Cloudflare Tunnel (required for podcast apps to accept custom feeds)

## Prerequisites

1. [Docker](https://www.docker.com/) and Docker Compose
2. [Google Books API Key](https://developers.google.com/books)
3. [Cloudflare account](https://www.cloudflare.com/) (for HTTPS access)
4. API access to an LLM (Ollama, OpenAI, Anthropic, or Groq)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd yt-audiobook-library
   ```

2. Create a `.env` file with required environment variables:
   ```
   APP_URL=https://your-domain.com

   # Database
   DB_NAME=ytbooks
   DB_USER=root
   DB_PASSWORD=rootpass

   # API Keys
   GOOGLE_BOOKS_API_KEY=your_google_books_api_key
   GOOGLE_API_KEY=your_google_api_key
   GROQ_API_KEY=your_groq_api_key  # or other LLM provider

   # App Config
   SECRET_KEY=your_secret_key
   DEBUG=True
   MIN_BOOK_DURATION=14400

   # Ollama (if using local LLM)
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   DEFAULT_OLLAMA_MODEL=gemma3
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

## Running the Application

### Start the app locally

```bash
docker-compose up
```

Access points:
- Frontend: http://localhost (port 80)
- Backend API: http://localhost:5001
- Adminer (database GUI): http://localhost:8081

### Start with HTTPS (Cloudflare Tunnel)

Podcast apps require HTTPS for custom podcast feeds. The easiest way to get HTTPS is with a Cloudflare Tunnel:

```bash
docker-compose up
./tunnel.sh
```

The app will be available at the URL configured in your Cloudflare Tunnel (set this as `APP_URL` in `.env`).

### Setting Up Cloudflare Tunnel

1. Install cloudflared:
   ```bash
   brew install cloudflared  # macOS
   ```

2. Login to Cloudflare:
   ```bash
   cloudflared tunnel login
   ```

3. Create a tunnel in the [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/):
   - Go to Networks > Tunnels
   - Create a new tunnel
   - Copy the tunnel token

4. Create `tunnel.sh`:
   ```bash
   #!/bin/bash
   cloudflared tunnel run --token YOUR_TUNNEL_TOKEN
   ```

5. Configure the public hostname in Zero Trust Dashboard:
   - Set hostname to your domain (e.g., `ytbooks.yourdomain.com`)
   - Set service to `http://localhost:80`

6. Update `.env` with your public URL:
   ```
   APP_URL=https://ytbooks.yourdomain.com
   ```

## Adding Audiobooks

Enter the Flask container and run commands:

```bash
docker-compose exec flask-app bash

# Full pipeline: scrape by author, category, general search, dedupe, and prune
flask add_books_full

# Add audiobooks by specific author
flask add_author "Author Name"

# Add audiobooks by category
flask add_books_by_category

# Remove duplicates (same title + author)
flask dedupe_books

# Remove audiobooks with deleted YouTube videos
flask prune_books
```

## Database Management

```bash
# Enter Flask container
docker-compose exec flask-app bash

# Create migration after model changes
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

### Check for duplicates

```sql
SELECT title, author_id, COUNT(*) AS num_occurrences
FROM audiobooks
GROUP BY title, author_id
HAVING COUNT(*) > 1
```

## Development

### Flask Interactive Shell

```bash
docker-compose exec flask-app bash
flask shell
ctx = app.test_request_context()
ctx.push()
load_ext autoreload
autoreload 2
```

### Frontend Development

The frontend runs with hot reload via Vite (HMR is disabled when using Cloudflare Tunnel):

```bash
docker-compose exec frontend sh
npm run dev
npm run build  # production build
npm run lint
```

## Project Structure

```
yt-audiobook-library/
├── flask_app/
│   ├── __init__.py          # App factory
│   ├── models.py            # SQLAlchemy models
│   ├── commands/            # Flask CLI commands
│   ├── routes/              # API blueprints
│   └── modules/             # Business logic
│       ├── youtube_crawler.py
│       ├── mp3_downloader.py
│       ├── google_books.py
│       └── llm/
├── frontend/
│   ├── src/
│   │   ├── pages/           # React page components
│   │   ├── components/      # Reusable components
│   │   ├── context/         # React context (auth)
│   │   └── api/             # API client
│   └── vite.config.js
├── docker-compose.yml
├── tunnel.sh                # Cloudflare tunnel runner
└── .env                     # Environment variables
```
