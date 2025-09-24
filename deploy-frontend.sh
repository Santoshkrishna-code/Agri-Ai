#!/bin/bash

echo "🚀 Starting Agri-AI Frontend Deployment..."

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found. Please run this script from the Agri-AI root directory."
    exit 1
fi

cd frontend

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH."
    exit 1
fi

echo "📦 Installing Node.js dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies."
    exit 1
fi

# Configure environment variables
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local
    echo "✅ Created .env.local with default API URL"
fi

echo ""
echo "✅ Frontend deployment ready!"
echo ""
echo "🎯 Available deployment options:"
echo ""
echo "1. Development server:"
echo "   npm run dev"
echo ""
echo "2. Production build and start:"
echo "   npm run build && npm start"
echo ""
echo "3. Build for static export:"
echo "   npm run build && npm run export"
echo ""

# Ask user which deployment method they prefer
read -p "Choose deployment method (1-3, or 'q' to quit): " choice

case $choice in
    1)
        echo "🚀 Starting development server..."
        echo "📍 Frontend will be available at: http://localhost:3000"
        echo "📍 Make sure backend is running at: http://localhost:5000"
        npm run dev
        ;;
    2)
        echo "🔨 Building for production..."
        npm run build
        if [ $? -eq 0 ]; then
            echo "🚀 Starting production server..."
            echo "📍 Frontend will be available at: http://localhost:3000"
            npm start
        else
            echo "❌ Build failed."
        fi
        ;;
    3)
        echo "🔨 Building for static export..."
        npm run build
        if [ $? -eq 0 ]; then
            echo "✅ Static build completed. Files are in the 'out' directory."
            echo "📁 You can serve these files with any static web server."
            echo ""
            echo "Example with Python:"
            echo "cd out && python -m http.server 3000"
            echo ""
            echo "Example with Node.js serve:"
            echo "npx serve out -p 3000"
        else
            echo "❌ Build failed."
        fi
        ;;
    q|Q)
        echo "👋 Deployment cancelled."
        ;;
    *)
        echo "❌ Invalid choice. Run the script again to choose a deployment method."
        ;;
esac

cd ..