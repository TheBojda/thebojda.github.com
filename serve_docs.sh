#!/bin/bash

# Default port
PORT=8080

# Check if a port number is provided as an argument
if [ $# -ge 1 ]; then
    PORT=$1
fi

# Check if the docs directory exists
if [ -d "docs" ]; then
    echo "Starting server on http://localhost:$PORT, serving from the docs directory..."
    python3 -m http.server "$PORT" --directory docs
else
    echo "Error: 'docs' directory not found."
    exit 1
fi
