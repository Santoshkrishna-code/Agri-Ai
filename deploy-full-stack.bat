@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Full Stack Agri-AI Deployment...

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo ❌ Error: backend\app.py not found. Please run this script from the Agri-AI root directory.
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: frontend directory not found. Please run this script from the Agri-AI root directory.
    exit /b 1
)

echo 📝 This script will deploy both backend and frontend services.
echo.
set /p confirm="Continue? (y/N): "
if /i not "!confirm!"=="y" (
    echo 👋 Deployment cancelled.
    exit /b 0
)

echo.
echo 🔧 Setting up Backend...
echo ================================

REM Backend setup
cd backend
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo ❌ Error: Failed to install backend dependencies.
    exit /b 1
)

if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env file with your actual credentials.
    echo Press any key after editing .env file...
    pause
)
cd ..

echo.
echo 🔧 Setting up Frontend...
echo ================================

cd frontend
npm install
if !errorlevel! neq 0 (
    echo ❌ Error: Failed to install frontend dependencies.
    exit /b 1
)

if not exist ".env.local" (
    echo NEXT_PUBLIC_API_URL=http://localhost:5000 > .env.local
    echo ✅ Created frontend environment file
)

echo 🔨 Building frontend...
npm run build
if !errorlevel! neq 0 (
    echo ❌ Error: Frontend build failed.
    exit /b 1
)

cd ..

echo.
echo ✅ Both services are ready for deployment!
echo.
echo 🎯 Deployment Options:
echo.
echo 1. Start both services (Backend: 5000, Frontend: 3000)
echo 2. Start backend only (Port 5000)
echo 3. Start frontend only (Port 3000)
echo 4. Docker Compose deployment
echo.

set /p choice="Choose deployment option (1-4): "

if "%choice%"=="1" (
    echo 🚀 Starting both services...
    start "Backend Server" cmd /c "cd backend && python app.py --host 0.0.0.0 --port 5000"
    timeout /t 3 /nobreak > nul
    start "Frontend Server" cmd /c "cd frontend && npm start"
    echo.
    echo ✅ Services started!
    echo 📍 Backend: http://localhost:5000
    echo 📍 Frontend: http://localhost:3000
    echo 📍 Health Check: http://localhost:5000/health
    echo.
    echo Press any key to stop all services...
    pause
    taskkill /f /im python.exe /t 2>nul
    taskkill /f /im node.exe /t 2>nul
) else if "%choice%"=="2" (
    echo 🚀 Starting backend only...
    cd backend
    python app.py --host 0.0.0.0 --port 5000
) else if "%choice%"=="3" (
    echo 🚀 Starting frontend only...
    cd frontend
    npm start
) else if "%choice%"=="4" (
    if exist "docker-compose.yml" (
        echo 🐳 Starting Docker Compose deployment...
        docker-compose up -d
        if !errorlevel! equ 0 (
            echo ✅ Docker services started!
            echo 📍 Frontend: http://localhost:3000
            echo 📍 Backend: http://localhost:5000
            echo.
            echo To stop services: docker-compose down
        ) else (
            echo ❌ Docker Compose failed to start services.
        )
    ) else (
        echo ❌ docker-compose.yml not found.
        echo Create it first or choose a different deployment option.
    )
) else (
    echo ❌ Invalid choice.
)

pause