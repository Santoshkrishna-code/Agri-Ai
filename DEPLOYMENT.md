# Deployment Guide for Agri-AI Application

This guide covers deployment options for both the backend Flask API and frontend Next.js application.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Backend Deployment](#backend-deployment)  
3. [Frontend Deployment](#frontend-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- Git

### Backend Setup (Flask API)

1. **Install Python dependencies:**
```bash
cd D:\Agri-Ai
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env with your actual values:
RF_API_KEY=9pTsuiQyAxjAJU7XL1sh
WORKSPACE_NAME=plant-ai-4q7oj
RICE_WORKFLOW_ID=custom-workflow-5
WHEAT_WORKFLOW_ID=custom-workflow-2
```

3. **Run the backend server:**
```bash
# Development mode
python app.py --debug

# Production mode
python app.py --host 0.0.0.0 --port 5000
```

### Frontend Setup (Next.js)

1. **Install Node.js dependencies:**
```bash
cd D:\Agri-Ai\frontend
npm install
```

2. **Configure frontend environment:**
```bash
# Create .env.local file
echo NEXT_PUBLIC_API_URL=http://localhost:5000 > .env.local
```

3. **Run the frontend development server:**
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Backend Deployment

### Option 1: Local Production Server

#### Using Gunicorn (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

# Or with custom configuration
gunicorn --config gunicorn.conf.py app:app
```

Create `gunicorn.conf.py`:
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### Using Docker
```bash
# Create Dockerfile for backend
cat > Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
EOF

# Build and run
docker build -t agri-ai-backend .
docker run -p 5000:5000 --env-file .env agri-ai-backend
```

### Option 2: Cloud Deployment

#### Deploy to Railway
1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy:
```bash
railway login
railway init
railway up
```

#### Deploy to Render
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: agri-ai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
    envVars:
      - key: RF_API_KEY
        value: 9pTsuiQyAxjAJU7XL1sh
      - key: WORKSPACE_NAME  
        value: plant-ai-4q7oj
      - key: RICE_WORKFLOW_ID
        value: custom-workflow-5
```

#### Deploy to Heroku
1. Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
```

2. Deploy:
```bash
heroku create agri-ai-backend
heroku config:set RF_API_KEY=9pTsuiQyAxjAJU7XL1sh
heroku config:set WORKSPACE_NAME=plant-ai-4q7oj  
heroku config:set RICE_WORKFLOW_ID=custom-workflow-5
git push heroku main
```

## Frontend Deployment

### Option 1: Local Production Build

```bash
cd D:\Agri-Ai\frontend

# Build for production
npm run build

# Start production server
npm start

# Or use PM2 for process management
npm install -g pm2
pm2 start npm --name "agri-ai-frontend" -- start
```

### Option 2: Static Site Generation

```bash
# Configure for static export in next.config.js
echo "/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig" > next.config.js

# Build and export
npm run build
```

### Option 3: Cloud Deployment

#### Deploy to Vercel (Recommended for Next.js)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd D:\Agri-Ai\frontend
vercel

# Configure environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

#### Deploy to Netlify
```bash
# Build the project
npm run build

# Deploy to Netlify (drag and drop the 'out' folder to Netlify)
# Or use Netlify CLI:
npm install -g netlify-cli
netlify deploy --prod --dir=out
```

#### Deploy with Docker
```bash
# Create Dockerfile for frontend
cat > frontend/Dockerfile << EOF
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
EOF

# Build and run
cd frontend
docker build -t agri-ai-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:5000 agri-ai-frontend
```

## Production Deployment

### Full Stack Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - RF_API_KEY=9pTsuiQyAxjAJU7XL1sh
      - WORKSPACE_NAME=plant-ai-4q7oj
      - RICE_WORKFLOW_ID=custom-workflow-5
      - WHEAT_WORKFLOW_ID=custom-workflow-2
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:5000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

### Nginx Configuration

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Backend API
        location /api/ {
            rewrite ^/api/(.*) /$1 break;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 300s;
            client_max_body_size 16M;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
```

### Deploy with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Configuration

### Backend Environment Variables (.env)
```env
# Required
RF_API_KEY=9pTsuiQyAxjAJU7XL1sh
WORKSPACE_NAME=plant-ai-4q7oj
RICE_WORKFLOW_ID=custom-workflow-5
WHEAT_WORKFLOW_ID=custom-workflow-2

# Optional
MIN_CONFIDENCE=0.4
CONFIDENCE_MARGIN=0.02
HOST=0.0.0.0
PORT=5000
DEBUG=false
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216
```

### Frontend Environment Variables (.env.local)
```env
# API URL - adjust based on your backend deployment
NEXT_PUBLIC_API_URL=http://localhost:5000

# For production
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Deployment Scripts

### Backend Deployment Script
Create `deploy-backend.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying Agri-AI Backend..."

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export RF_API_KEY="9pTsuiQyAxjAJU7XL1sh"
export WORKSPACE_NAME="plant-ai-4q7oj"
export RICE_WORKFLOW_ID="custom-workflow-5"
export WHEAT_WORKFLOW_ID="custom-workflow-2"

# Test the API
python -c "from app import create_inference_client; print('✅ API client created successfully')"

# Start with gunicorn
echo "Starting backend server..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Frontend Deployment Script
Create `deploy-frontend.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying Agri-AI Frontend..."

cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local

# Build for production
npm run build

# Start production server
npm start
```

Make scripts executable:
```bash
chmod +x deploy-backend.sh
chmod +x deploy-frontend.sh
```

## Troubleshooting

### Common Backend Issues

1. **Port already in use:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <process_id> /F
```

2. **API Key errors:**
```bash
# Test API credentials
python test_rice_api.py
```

3. **Memory issues:**
```bash
# Reduce workers in gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

### Common Frontend Issues

1. **Build failures:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

2. **API connection issues:**
```bash
# Check if backend is running
curl http://localhost:5000/health
```

3. **Environment variables not loading:**
```bash
# Ensure .env.local exists in frontend directory
ls -la frontend/.env.local
```

### Monitoring and Logs

#### Backend Logging
```bash
# Enable file logging
export LOG_FILE="/var/log/agri-ai/app.log"
export LOG_LEVEL="INFO"

# View logs
tail -f /var/log/agri-ai/app.log
```

#### Frontend Logging
```bash
# View Next.js logs
npm run dev 2>&1 | tee frontend.log
```

#### Docker Logs
```bash
# View container logs
docker logs agri-ai-backend -f
docker logs agri-ai-frontend -f
```

## Security Considerations

### Backend Security
- Use HTTPS in production
- Implement rate limiting
- Validate file uploads
- Keep API keys secure
- Use environment variables for secrets

### Frontend Security  
- Sanitize user inputs
- Use HTTPS
- Implement CORS properly
- Validate API responses

### Example Security Headers (Nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Performance Optimization

### Backend Optimization
- Use connection pooling
- Implement caching
- Optimize image processing
- Use async processing for long tasks

### Frontend Optimization
- Enable image optimization
- Use code splitting
- Implement lazy loading
- Optimize bundle size

## Monitoring and Health Checks

### Health Check Endpoints
```bash
# Backend health
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "service": "agri-ai-inference",
  "version": "1.0.0"
}
```

### Monitoring Script
Create `health-check.sh`:
```bash
#!/bin/bash

# Check backend
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"  
else
    echo "❌ Frontend is down"
fi
```

This comprehensive deployment guide should help you deploy your Agri-AI application in various environments. Choose the deployment method that best fits your needs and infrastructure requirements.