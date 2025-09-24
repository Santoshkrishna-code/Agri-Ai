#!/bin/bash

echo "🚀 Starting Agri-AI Backend Deployment..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the Agri-AI root directory."
    exit 1
fi

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your actual credentials before proceeding."
    exit 1
fi

# Test API configuration
echo "🔍 Testing API configuration..."
python -c "
from app import create_inference_client, Config
try:
    client = create_inference_client()
    print('✅ API client created successfully')
    print(f'   API URL: {Config.RF_API_URL}')
    print(f'   Workspace: {Config.WORKSPACE_NAME}')
    print(f'   Rice Workflow: {Config.RICE_WORKFLOW_ID}')
except Exception as e:
    print(f'❌ API configuration error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Error: API configuration test failed."
    exit 1
fi

# Check if gunicorn is installed
if ! pip show gunicorn &> /dev/null; then
    echo "📦 Installing Gunicorn..."
    pip install gunicorn
fi

echo ""
echo "✅ Backend deployment ready!"
echo ""
echo "🎯 Available deployment options:"
echo ""
echo "1. Development server:"
echo "   python app.py --debug"
echo ""
echo "2. Production server (Gunicorn):"
echo "   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"
echo ""
echo "3. Docker deployment:"
echo "   docker build -t agri-ai-backend ."
echo "   docker run -p 5000:5000 --env-file .env agri-ai-backend"
echo ""

# Ask user which deployment method they prefer
read -p "Choose deployment method (1-3, or 'q' to quit): " choice

case $choice in
    1)
        echo "🚀 Starting development server..."
        python app.py --debug
        ;;
    2)
        echo "🚀 Starting production server with Gunicorn..."
        gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
        ;;
    3)
        echo "🐳 Building Docker image..."
        docker build -t agri-ai-backend .
        if [ $? -eq 0 ]; then
            echo "🚀 Starting Docker container..."
            docker run -p 5000:5000 --env-file .env agri-ai-backend
        else
            echo "❌ Docker build failed."
        fi
        ;;
    q|Q)
        echo "👋 Deployment cancelled."
        ;;
    *)
        echo "❌ Invalid choice. Run the script again to choose a deployment method."
        ;;
esac