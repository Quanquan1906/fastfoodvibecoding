@echo off
REM FastFood Demo - Startup Script for Windows
echo.
echo ================================
echo   🍔 FastFood Delivery System 🚁
echo ================================
echo.

echo 🔍 Checking MongoDB connection...
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MongoDB not found. Please install MongoDB first.
    pause
    exit /b 1
)

echo ✅ MongoDB found
echo.
echo Starting services...
echo.

REM Start MongoDB in background
echo 🟢 Starting MongoDB...
start "MongoDB" mongod

REM Start Backend
echo 🔵 Starting Backend (FastAPI)...
cd backend
start "FastAPI Backend" cmd /k "python -m pip install -q -r requirements.txt & uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start Frontend
echo 🟡 Starting Frontend (React)...
cd ..\frontend
start "React Frontend" cmd /k "npm install -q & npm start"

echo.
echo ================================
echo ✅ All services started!
echo ================================
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔌 Backend:  http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo Press CTRL+C in any window to stop services
pause
