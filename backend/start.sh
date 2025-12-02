#!/bin/bash

# Start FastAPI server in background immediately to satisfy Render timeout
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
API_PID=$!

# Install Playwright & Start Worker in background
(
  echo "Installing Playwright browsers (Chromium only)..."
  playwright install chromium
  
  echo "Starting ARQ worker..."
  arq app.worker.WorkerSettings > worker.log 2>&1
) &

# Wait for API to finish (keep container alive)
wait $API_PID
