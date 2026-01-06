#!/bin/bash

# Start script for Navigation System
# Starts both Flask API and React frontend

echo "🚀 Starting Photo-Based Navigation System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. AI features may not work."
fi

# Start Flask API in background
echo "📡 Starting Flask API server..."
python3 api_server.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start React frontend
echo "⚛️  Starting React frontend..."
cd web-app
npm run dev &
REACT_PID=$!

echo ""
echo "✅ System started!"
echo "📍 API Server: http://localhost:5000"
echo "🌐 Web App: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $FLASK_PID $REACT_PID 2>/dev/null; exit" INT TERM
wait

