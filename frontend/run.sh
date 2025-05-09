#!/bin/bash

# Start Flask server in the background
cd /app
flask run --host=0.0.0.0 &
FLASK_PID=$!

# Start React development server
cd /app/frontend
npm run dev

# When React server stops, kill Flask server
kill $FLASK_PID
