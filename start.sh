#!/bin/bash

# FastFood Demo - Startup Script for macOS/Linux

echo ""
echo "================================"
echo "  🍔 FastFood Delivery System 🚁"
echo "================================"
echo ""

echo "🔍 Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB not found. Please install MongoDB first."
    echo "   On macOS: brew install mongodb-community"
    echo "   On Linux: Follow https://docs.mongodb.com/manual/installation/"
    exit 1
fi

echo "✅ MongoDB found"
echo ""
echo "Starting services..."
echo ""

# Start MongoDB
echo "🟢 Starting MongoDB..."
mongod &
MONGO_PID=$!

# Wait for MongoDB to start
sleep 2

# Start Backend
echo "🔵 Starting Backend (FastAPI)..."
cd backend
python -m pip install -q -r requirements.txt 2>/dev/null
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo "🟡 Starting Frontend (React)..."
cd ../frontend
npm install -q 2>/dev/null
npm start &
FRONTEND_PID=$!

echo ""
echo "================================"
echo "✅ All services started!"
echo "================================"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop all services"
echo ""

# Keep script running
wait
