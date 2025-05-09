Run aider

aider --model o3-mini --api-key openai=$OPENAI_API_KEY --chat-language en
aider --model gemini/gemini-2.5-pro-exp-03-25

Bring up docker image

docker-compose up --build

Run a flask command in the container

docker-compose exec flask-app flask add_books "audiobook"

## FLASK INTERACTIVE SHELL

for development you can use the flask interactive shell REPL. Unfortunately it does not live-reload when file changes are made.
From WITHIN the docker container:

flask shell
ctx = app.test_request_context()
ctx.push()
load_ext autoreload
autoreload 2
