#!/bin/bash

# Start the ARQ worker in the background and log to file
echo "Starting ARQ worker..."
arq app.worker.WorkerSettings > worker.log 2>&1 &

# Start the FastAPI application in the foreground
echo "Starting FastAPI server..."
# Use exec to let uvicorn take over the PID 1 (or the shell's PID) for signal handling
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
