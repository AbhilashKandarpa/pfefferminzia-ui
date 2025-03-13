#!/bin/bash

# Ensure we're in the correct directory
cd /app || exit 1

# Start the FastAPI backend server
python -m uvicorn server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start and verify it's running
sleep 5
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start"
    exit 1
fi

# Start the React frontend
cd /app/frontend || exit 1
npm start