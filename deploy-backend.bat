@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Agri-AI Backend Deployment...

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo ❌ Error: backend\app.py not found. Please run this script from the Agri-AI root directory.
    exit /b 1
)

REM Change to backend directory
cd backend

REM Check Python installation
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Error: Python is not installed or not in PATH.
    exit /b 1
)

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if !errorlevel! neq 0 (
    echo ❌ Error: Failed to install dependencies.
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env file with your actual credentials before proceeding.
    pause
    exit /b 1
)

REM Test API configuration
echo 🔍 Testing API configuration...
python -c "from app import create_inference_client, Config; client = create_inference_client(); print('✅ API client created successfully'); print(f'   API URL: {Config.RF_API_URL}'); print(f'   Workspace: {Config.WORKSPACE_NAME}'); print(f'   Rice Workflow: {Config.RICE_WORKFLOW_ID}')"

if !errorlevel! neq 0 (
    echo ❌ Error: API configuration test failed.
    exit /b 1
)

REM Check if gunicorn is installed
pip show gunicorn >nul 2>&1
if !errorlevel! neq 0 (
    echo 📦 Installing Gunicorn...
    pip install gunicorn
)

echo.
echo ✅ Backend deployment ready!
echo.
echo 🎯 Available deployment options:
echo.
echo 1. Development server:
echo    python app.py --debug
echo.
echo 2. Production server (Gunicorn):
echo    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
echo.
echo 3. Simple Python server:
echo    python app.py --host 0.0.0.0 --port 5000
echo.

REM Ask user which deployment method they prefer
set /p choice="Choose deployment method (1-3, or 'q' to quit): "

if "%choice%"=="1" (
    echo 🚀 Starting development server...
    python app.py --debug
) else if "%choice%"=="2" (
    echo 🚀 Starting production server with Gunicorn...
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
) else if "%choice%"=="3" (
    echo 🚀 Starting simple Python server...
    python app.py --host 0.0.0.0 --port 5000
) else if /i "%choice%"=="q" (
    echo 👋 Deployment cancelled.
) else (
    echo ❌ Invalid choice. Run the script again to choose a deployment method.
)

cd ..
pause