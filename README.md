# PROJECT OVERVIEW

This application has two parts: a process that scrapes youtube for audiobooks and categorizes them in a Postgres database, and a React front-end that let's you search and browse the library.

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
