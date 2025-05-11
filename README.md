# PROJECT OVERVIEW

This application has two parts: a process that scrapes youtube for audiobooks and categorizes them in a Postgres database, and a React front-end that let's you search and browse the library.

## YOUTUBE SCRAPER

The scraper searches YouTube using playwright via the normal browser UI - Google has a YouTube Data API but the limits are ridiculously low. There are some attempts made to make the visit look human, like throttling the speed and varying the user agent.

The crawler finds audiobooks by using various searches

1.  'intitle:"audiobook" [category]' - where category is one of a list of predefined categories in the database e.g. "History".
2.  'intitle:"audiobook" [author]' - where author is one of a list of predefined authors in the database e.g. "Kurt Vonnegut". There are about 200 authors seeded in the data.
3.  'intitle:"audiobook"' - just find any vide with "audiobook" in the title.

Since Youtube isn't for audiobooks specifically, parsing out what the actual book title and author is a challenge. Example:

"Goldfinger by Ian Fleming Read by Hugh Bonneville | FULL AUDIOBOOK"

I pass the title and description to an LLM (Ollama/Qwen) to reason out the book title and author. But even after that, there's still alot of trash. So I take that information and I search the Google Books API to see if it actually is a book. I then take all of the informatioon gathered and ask the LLM to categorize the book in one (or more) of the pre-defined categories.

## PREREQUISITES

1.  [Docker](https://www.docker.com/)
2.  [Google Books API Access](https://developers.google.com/books)
3.  API access to an LLM

## UPDATING THE DATA

## DE-DUPING THE DATA

This query will show how many dupes there are:

`SELECT title, author_id, COUNT(*) AS num_occurrences
FROM audiobooks
GROUP BY title, author_id
HAVING COUNT(*) > 1`

this command will dedupe the audiobooks

`flask dedupe_books`

## FLASK INTERACTIVE SHELL

for development you can use the flask interactive shell REPL. Unfortunately it does not live-reload when file changes are made.
From WITHIN the docker container:

flask shell
ctx = app.test_request_context()
ctx.push()
load_ext autoreload
autoreload 2
