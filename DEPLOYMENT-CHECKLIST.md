# 🚀 Agri-AI Deployment Checklist

Follow these steps exactly to deploy your application:

## ✅ Pre-Deployment Checklist

**Check these first:**
- [ ] Python is installed: Open PowerShell and run `python --version`
- [ ] Node.js is installed: Run `node --version`
- [ ] You're in the correct directory: `cd "D:\Agri-Ai"`

**If any are missing, install them first:**
- Python: https://python.org/downloads/
- Node.js: https://nodejs.org/

---

## 🔧 Backend Deployment (5 minutes)

**Step 1:** Open PowerShell as Administrator

**Step 2:** Navigate to your project
```
cd "D:\Agri-Ai"
```

**Step 3:** Run backend deployment
```
.\deploy-backend.bat
```

**Step 4:** When prompted, choose:
- **Option 1** for development (easier, shows all logs)
- **Option 2** for production (faster, more stable)

**Step 5:** Verify backend is working
- Open browser: http://localhost:5000/health
- Should show: `{"status":"healthy"}`

✅ **Backend Complete!**

---

## 🎨 Frontend Deployment (5 minutes)

**Step 1:** Open a NEW PowerShell window

**Step 2:** Navigate to your project
```
cd "D:\Agri-Ai"
```

**Step 3:** Run frontend deployment
```
.\deploy-frontend.bat
```

**Step 4:** When prompted, choose:
- **Option 1** for development (with hot reload)
- **Option 2** for production (optimized build)

**Step 5:** Verify frontend is working
- Open browser: http://localhost:3000
- Should show the Agri-AI interface

✅ **Frontend Complete!**

---

## 🧪 Test Your Application

**Step 1:** Go to http://localhost:3000

**Step 2:** Upload a rice image

**Step 3:** Check if detection works

**Step 4:** Verify results appear

✅ **Testing Complete!**

---

## 🔄 Alternative: One-Click Deployment

If you want to deploy both at once:

```
cd "D:\Agri-Ai"
.\deploy-full-stack.bat
```

Choose option 1 to start both services.

---

## 🚨 If Something Goes Wrong

### Problem: "Execution policy error"
**Solution:**
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Python not found"
**Solution:**
1. Install Python from https://python.org
2. Make sure to check "Add Python to PATH"
3. Restart PowerShell

### Problem: "Node not found"
**Solution:**
1. Install Node.js from https://nodejs.org
2. Restart PowerShell

### Problem: "Port already in use"
**Solution:**
```
netstat -ano | findstr :5000
taskkill /PID <number> /F
```

### Problem: "API not working"
**Solution:**
1. Check your .env file exists
2. Make sure it has the correct API key: `9pTsuiQyAxjAJU7XL1sh`

---

## 📍 Important URLs

After deployment, bookmark these:

- **Frontend App:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **API Test:** http://localhost:5000/predict

---

## 🛑 How to Stop Services

**To stop everything:**
```
taskkill /f /im python.exe
taskkill /f /im node.exe
```

**Or just close the PowerShell windows.**

---

## ✨ Success! What Next?

Once everything is working:

1. **Bookmark:** http://localhost:3000
2. **Test with different images**
3. **Share with your team**
4. **Consider cloud deployment for production**

**You now have a fully working AI-powered rice detection system!** 🌾

---

## 📞 Need Help?

1. Check error messages carefully
2. Look at the PowerShell output
3. Try restarting the deployment scripts
4. Make sure all prerequisites are installed

**Most common fix:** Restart PowerShell as Administrator and try again.