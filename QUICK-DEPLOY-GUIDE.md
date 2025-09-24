# Quick Deployment Guide for Agri-AI

This is a simple step-by-step guide to deploy your Agri-AI application locally and in production.

## 🚀 Quick Start (5 minutes)

### Step 1: Deploy Backend (Flask API)

1. **Open PowerShell as Administrator**
2. **Navigate to your project:**
   ```powershell
   cd "D:\Agri-Ai"
   ```

3. **Run the backend deployment script:**
   ```powershell
   .\deploy-backend.bat
   ```
   
4. **The script will:**
   - Install Python dependencies
   - Check your configuration
   - Test the API connection
   - Give you deployment options

5. **Choose option 1 for development** or **option 2 for production**

6. **Your backend will be running at:** `http://localhost:5000`

### Step 2: Deploy Frontend (Next.js)

1. **Open a NEW PowerShell window**
2. **Navigate to your project:**
   ```powershell
   cd "D:\Agri-Ai"
   ```

3. **Run the frontend deployment script:**
   ```powershell
   .\deploy-frontend.bat
   ```

4. **The script will:**
   - Install Node.js dependencies
   - Configure environment variables
   - Build the application
   - Give you deployment options

5. **Choose option 1 for development** or **option 2 for production**

6. **Your frontend will be available at:** `http://localhost:3000`

### Step 3: Test Your Application

1. **Open your browser and go to:** `http://localhost:3000`
2. **Upload an image to test the rice detection**
3. **Check the backend health:** `http://localhost:5000/health`

---

## 🔧 Alternative: One-Command Deployment

If you want to deploy both services at once:

```powershell
cd "D:\Agri-Ai"
.\deploy-full-stack.bat
```

This will start both backend and frontend automatically.

---

## 📋 Prerequisites Check

Before deployment, make sure you have:

### Required Software:
- ✅ **Python 3.8+** - Check: `python --version`
- ✅ **Node.js 18+** - Check: `node --version`
- ✅ **npm** - Check: `npm --version`
- ✅ **Git** - Check: `git --version`

### Install Missing Software:
- **Python:** Download from [python.org](https://python.org/downloads/)
- **Node.js:** Download from [nodejs.org](https://nodejs.org/)

---

## ⚙️ Configuration

### Backend Configuration (.env file):
Your `.env` file should contain:
```env
RF_API_KEY=9pTsuiQyAxjAJU7XL1sh
WORKSPACE_NAME=plant-ai-4q7oj
RICE_WORKFLOW_ID=custom-workflow-5
WHEAT_WORKFLOW_ID=custom-workflow-2
MIN_CONFIDENCE=0.4
HOST=0.0.0.0
PORT=5000
```

### Frontend Configuration:
The deployment script automatically creates `.env.local` with:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. "Python not found"
**Solution:**
```powershell
# Add Python to PATH or reinstall Python with "Add to PATH" checked
```

#### 2. "Node.js not found"
**Solution:**
```powershell
# Install Node.js from nodejs.org and restart PowerShell
```

#### 3. "Port already in use"
**Solution:**
```powershell
# Find and kill process using the port
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

#### 4. "Permission denied"
**Solution:**
```powershell
# Run PowerShell as Administrator
# Or change execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 5. "API connection failed"
**Solution:**
- Check your `.env` file has correct API credentials
- Test API manually: `python test_rice_api.py`

---

## 🌐 Production Deployment Options

### Option 1: Cloud Deployment (Easiest)

#### Backend on Railway:
1. **Install Railway CLI:**
   ```powershell
   npm install -g @railway/cli
   ```
2. **Deploy:**
   ```powershell
   railway login
   railway init
   railway up
   ```

#### Frontend on Vercel:
1. **Install Vercel CLI:**
   ```powershell
   npm install -g vercel
   ```
2. **Deploy:**
   ```powershell
   cd frontend
   vercel
   ```

### Option 2: Docker Deployment

1. **Create docker-compose.yml** (already provided)
2. **Run:**
   ```powershell
   docker-compose up -d
   ```

### Option 3: VPS/Server Deployment

1. **Use provided Linux scripts:**
   - `deploy-backend.sh`
   - `deploy-frontend.sh`

2. **Copy files to server:**
   ```bash
   scp -r D:\Agri-Ai user@your-server:/path/to/deployment
   ```

---

## 📊 Monitoring

### Health Checks:
- **Backend Health:** `http://localhost:5000/health`
- **Frontend:** `http://localhost:3000`

### Logs:
- **Backend logs:** Check PowerShell window
- **Frontend logs:** Check browser console

### Performance:
- **API Response Time:** Use browser dev tools
- **Memory Usage:** Check Task Manager

---

## 🔐 Security (Production Only)

### Backend Security:
1. **Change default ports**
2. **Use HTTPS certificates**
3. **Set up firewall rules**
4. **Use environment variables for secrets**

### Frontend Security:
1. **Enable HTTPS**
2. **Configure CORS properly**
3. **Use secure headers**

---

## 📞 Support

### If you encounter issues:

1. **Check the error message carefully**
2. **Look in the troubleshooting section above**
3. **Check log files**
4. **Verify all prerequisites are installed**

### Common Commands:
```powershell
# Check if services are running
netstat -ano | findstr :5000  # Backend
netstat -ano | findstr :3000  # Frontend

# Stop services
taskkill /f /im python.exe    # Stop backend
taskkill /f /im node.exe      # Stop frontend

# Restart deployment
.\deploy-full-stack.bat
```

---

## 🎯 Success Checklist

After successful deployment, you should have:

- ✅ Backend API running at `http://localhost:5000`
- ✅ Frontend app running at `http://localhost:3000`
- ✅ Health check responding at `http://localhost:5000/health`
- ✅ Image upload working on frontend
- ✅ Rice detection API responding correctly

### Test Your Deployment:
1. Go to `http://localhost:3000`
2. Upload a rice image
3. Verify detection results
4. Check `http://localhost:5000/health` returns `{"status":"healthy"}`

---

**🎉 Congratulations! Your Agri-AI application is now deployed and ready to use!**