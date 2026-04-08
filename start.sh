#!/bin/bash
# AuraScore orchestrator script
echo "Starting AuraScore..."

# Cleanup hooks
cleanup() {
    echo "Stopping services..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    lsof -ti :5173 | xargs kill -9 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Checking ports..."
lsof -ti :8000 | xargs kill -9 2>/dev/null
lsof -ti :5173 | xargs kill -9 2>/dev/null

echo "Starting Backend (FastAPI)..."
cd backend
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/aurascore_backend.log 2>&1 &
cd ..

# Health check
echo "Waiting for backend to be ready..."
while ! lsof -ti :8000 > /dev/null; do
    sleep 1
done
echo "Backend is running!"

echo "Starting Frontend (Vite React)..."
cd frontend
nohup npm run dev > /tmp/aurascore_frontend.log 2>&1 &
cd ..

echo "Waiting for frontend to be ready..."
while ! lsof -ti :5173 > /dev/null; do
    sleep 1
done
echo "Frontend is running at http://localhost:5173"
echo "Press Ctrl+C to stop all services."

wait
