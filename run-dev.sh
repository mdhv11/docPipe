#!/bin/bash

# docPipe development runner
# Starts both backend and frontend services

echo "Starting docPipe development environment..."

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
	echo "Setting up Python virtual environment..."
	cd backend
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	cd ..
fi

# Start backend in background
echo "Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in background
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
