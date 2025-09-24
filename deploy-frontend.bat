@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Agri-AI Frontend Deployment...

REM Check if we're in the right directory
if not exist "frontend" (
    echo ❌ Error: frontend directory not found. Please run this script from the Agri-AI root directory.
    exit /b 1
)

cd frontend

REM Check Node.js installation
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Error: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Check npm installation
npm --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Error: npm is not installed or not in PATH.
    exit /b 1
)

echo 📦 Installing Node.js dependencies...
npm install

if !errorlevel! neq 0 (
    echo ❌ Error: Failed to install dependencies.
    exit /b 1
)

REM Configure environment variables
if not exist ".env.local" (
    echo 📝 Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:5000 > .env.local
    echo ✅ Created .env.local with default API URL
)

echo.
echo ✅ Frontend deployment ready!
echo.
echo 🎯 Available deployment options:
echo.
echo 1. Development server:
echo    npm run dev
echo.
echo 2. Production build and start:
echo    npm run build ^&^& npm start
echo.
echo 3. Build for static export:
echo    npm run build ^&^& npm run export
echo.

REM Ask user which deployment method they prefer
set /p choice="Choose deployment method (1-3, or 'q' to quit): "

if "%choice%"=="1" (
    echo 🚀 Starting development server...
    echo 📍 Frontend will be available at: http://localhost:3000
    echo 📍 Make sure backend is running at: http://localhost:5000
    npm run dev
) else if "%choice%"=="2" (
    echo 🔨 Building for production...
    npm run build
    if !errorlevel! equ 0 (
        echo 🚀 Starting production server...
        echo 📍 Frontend will be available at: http://localhost:3000
        npm start
    ) else (
        echo ❌ Build failed.
    )
) else if "%choice%"=="3" (
    echo 🔨 Building for static export...
    npm run build
    if !errorlevel! equ 0 (
        echo ✅ Static build completed. Files are in the 'out' directory.
        echo 📁 You can serve these files with any static web server.
        echo.
        echo Example with Python:
        echo cd out ^&^& python -m http.server 3000
        echo.
        echo Example with Node.js serve:
        echo npx serve out -p 3000
    ) else (
        echo ❌ Build failed.
    )
) else if /i "%choice%"=="q" (
    echo 👋 Deployment cancelled.
) else (
    echo ❌ Invalid choice. Run the script again to choose a deployment method.
)

cd ..
pause