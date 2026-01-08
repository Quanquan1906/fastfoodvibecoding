# 📋 Installation Guide

Complete step-by-step setup instructions for all operating systems.

## Prerequisites

### Minimum Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 1GB free space

### Required Software

1. **MongoDB 5.0+**
   - Download: https://www.mongodb.com/try/download/community
   - Size: ~300MB

2. **Python 3.9+**
   - Download: https://www.python.org/downloads/
   - Size: ~100MB

3. **Node.js 18+ & npm**
   - Download: https://nodejs.org/
   - Size: ~150MB

---

## Step 1: Install MongoDB

### Windows
1. Download installer from https://www.mongodb.com/try/download/community
2. Run the installer
3. Choose "Install MongoDB as a Service" (recommended)
4. Complete installation

**Verify:**
```bash
mongod --version
```

### macOS (Homebrew - Recommended)
```bash
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

**Verify:**
```bash
mongod --version
```

### Linux (Ubuntu/Debian)
```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Install
sudo apt-get update
sudo apt-get install mongodb-org

# Start
sudo systemctl start mongod
```

**Verify:**
```bash
mongod --version
```

---

## Step 2: Install Python & Dependencies

### Windows
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**Verify:**
```bash
python --version
pip --version
```

### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify
python3 --version
pip3 --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Verify
python3 --version
pip3 --version
```

---

## Step 3: Install Node.js & npm

### Windows, macOS, Linux
1. Download from https://nodejs.org/ (LTS version recommended)
2. Run installer and follow prompts
3. npm is installed automatically with Node.js

**Verify:**
```bash
node --version
npm --version
```

Should show v18+ for Node and 9+ for npm

---

## Step 4: Clone/Download FastFood Project

```bash
# If using git
git clone <repository-url>
cd FastFood

# Or manually download and extract the project folder
```

---

## Step 5: Setup Backend

### All Platforms

```bash
# Navigate to backend
cd FastFood/backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if all packages installed correctly
pip list
```

**Expected packages:**
- fastapi
- uvicorn
- motor
- pymongo
- pydantic
- python-dotenv

---

## Step 6: Setup Frontend

### All Platforms

```bash
# Navigate to frontend
cd FastFood/frontend

# Install dependencies (first time only)
npm install

# Verify dependencies
npm list react react-router-dom axios
```

**Expected packages:**
- react 19.x
- react-router-dom 6.x
- axios 1.x

---

## ✅ Verify Installation

Run these commands to verify everything is installed:

```bash
# Check MongoDB
mongod --version
# Should output: db version v5.0.0 or later

# Check Python
python --version
# Should output: Python 3.9 or later

# Check pip packages
pip show fastapi uvicorn motor pymongo
# Should show installed packages

# Check Node.js
node --version
# Should output: v18 or later

# Check npm
npm --version
# Should output: 9 or later
```

---

## 🚀 Start the Application

### Quick Start (All-in-One)

**Windows:**
```bash
cd FastFood
start.bat
```

**macOS/Linux:**
```bash
cd FastFood
chmod +x start.sh
./start.sh
```

### Manual Start

**Terminal 1 - MongoDB:**
```bash
mongod
```

**Terminal 2 - Backend:**
```bash
cd FastFood/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd FastFood/frontend
npm start
```

---

## 🎯 Expected Output

### Backend Success
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     ✅ Connected to MongoDB: foodfast
```

### Frontend Success
```
Compiled successfully!
Local:            http://localhost:3000
```

### Browser
Page should load with purple gradient login screen

---

## 🧪 Test Connection

### MongoDB
```bash
mongo  # or mongosh on newer versions
> db.version()
# Should return version number
> exit
```

### Backend API
```bash
curl http://localhost:8000/health
# Should return: {"status":"✅ FastFood API is running"}
```

### Frontend
Open http://localhost:3000 in browser
- Should see login page
- Should be able to enter username
- Should be able to select role

---

## 🆘 Troubleshooting Installation

### "Python not found"
- Ensure Python is added to PATH
- Restart terminal/shell
- Use `python3` instead of `python` on macOS/Linux

### "pip install fails"
```bash
# Upgrade pip first
pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

### "MongoDB connection refused"
- Ensure `mongod` is running in separate terminal
- Check if port 27017 is not blocked by firewall
- On Windows: Check if MongoDB service is running

### "npm install takes too long"
- Normal on first install (can take 2-5 minutes)
- Check internet connection
- Try: `npm cache clean --force`

### "Port already in use"
```bash
# Find and kill process using port
# Windows: 
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### "Virtual environment issues"
```bash
# Delete and recreate venv
rm -rf venv  # Linux/macOS: rm -rf, Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📊 Installation Checklist

- [ ] MongoDB installed and running
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] FastFood project folder exists
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] All three services can start
- [ ] Browser opens to http://localhost:3000
- [ ] Can login successfully

---

## 🎉 You're Ready!

Once all items are checked, you can proceed to the Quick Start Guide.

If you encounter any issues, check the [QUICK_START.md](./QUICK_START.md) troubleshooting section.

---

## 📚 Additional Resources

- **MongoDB Installation**: https://docs.mongodb.com/manual/installation/
- **Python Setup**: https://docs.python.org/3/using/index.html
- **Node.js Documentation**: https://nodejs.org/en/docs/
- **FastAPI Guide**: https://fastapi.tiangolo.com/
- **React Tutorial**: https://react.dev/learn

---

**Happy Installation! 🎉**
