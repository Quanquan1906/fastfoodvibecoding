# 🚀 FastFood System - Quick Start Guide

## ⚡ Fastest Way to Get Running

### Option 1: Automated Scripts (Recommended)

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

Then open your browser to `http://localhost:3000`

---

### Option 2: Manual Setup (Step by Step)

#### Step 1: Start MongoDB
```bash
# Make sure MongoDB is running
mongod
```

#### Step 2: Start Backend
```bash
cd FastFood/backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Application startup complete
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to see API documentation

#### Step 3: Start Frontend
```bash
# In another terminal
cd FastFood/frontend

# Install dependencies (first time only)
npm install

# Start React dev server
npm start
```

Browser will automatically open to [http://localhost:3000](http://localhost:3000)

---

## 🎬 How to Use

### 1️⃣ **Customer Journey** (5 minutes)
1. Login page → Enter any username, select "CUSTOMER" → Login
2. Browse restaurants
3. Click "View Menu" on a restaurant
4. Add items to cart
5. Click "Place Order"
6. Click "Mock Payment" ✅
7. Watch the fake drone movement
8. See order complete in real-time ✨

### 2️⃣ **Restaurant Journey** (5 minutes)
1. Login → Enter any username, select "RESTAURANT" → Login
2. Go to "Orders" tab
3. See incoming orders (from customers)
4. Click "✅ Accept" to accept a pending order
5. Click "📦 Ready" when food is prepared
6. (Admin will assign drone from admin panel)

### 3️⃣ **Admin Journey** (10 minutes)
1. Login → Enter any username, select "ADMIN" → Login
2. **Restaurants Tab**: 
   - Create restaurants
   - Assign owners
3. **Drones Tab**:
   - Create drones for restaurants
4. **Users Tab**:
   - View all system users
5. **Orders Tab**:
   - Monitor all orders system-wide

---

## 🧪 Test Scenarios

### Test Complete Order Flow:
1. **Admin**: Create 2 restaurants and assign drones
2. **Customer**: Order from first restaurant
3. **Restaurant**: Accept and prepare order
4. **Admin**: Assign drone to order
5. **Customer**: Watch real-time delivery
6. **System**: Order auto-completes

### Test Multi-User:
- Open 3 browser tabs
- Login as Customer, Restaurant, Admin in each
- Make order as customer
- Accept as restaurant
- Assign drone as admin
- Watch all roles see updates in real-time

---

## ✅ Verification Checklist

After startup, verify everything is working:

- [ ] MongoDB running: `mongod --version`
- [ ] Backend running: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- [ ] Frontend running: Open [http://localhost:3000](http://localhost:3000)
- [ ] Login page loads
- [ ] Can login with any username
- [ ] Can browse restaurants as customer
- [ ] Can create menu items as restaurant
- [ ] Can create restaurants as admin

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| MongoDB won't start | Install MongoDB first: [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/) |
| Port 8000 in use | Kill process: `lsof -ti:8000 \| xargs kill -9` (macOS/Linux) |
| Port 3000 in use | Kill process: `lsof -ti:3000 \| xargs kill -9` (macOS/Linux) |
| `pip: command not found` | Install Python 3.9+: [https://www.python.org](https://www.python.org) |
| `npm: command not found` | Install Node.js 18+: [https://nodejs.org](https://nodejs.org) |
| WebSocket errors | Restart backend - WebSocket connection is being established |
| CORS errors | Already configured - clear browser cache or use incognito mode |

---

## 📊 System URLs

Once everything is running:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## 🎯 Next Steps

1. **Explore the API**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Read the Code**: Check `backend/app/api/routes.py` for all endpoints
3. **Understand the Flow**: See `backend/app/services/` for business logic
4. **Customize**: Modify prices, restaurant names, drone speeds, etc.

---

## 📚 Demo Features

✅ **3 User Roles**: Customer, Restaurant, Admin
✅ **Real-time Updates**: WebSocket order tracking
✅ **Fake Drone**: Simulated GPS movement
✅ **Mock Payment**: Always succeeds
✅ **Multi-Tenant**: Multiple restaurants
✅ **Simple Auth**: No password needed
✅ **Full UI**: Complete frontend included

---

## 🎉 You're Ready!

Everything is set up and ready to go. Start the services and enjoy the demo! 🚀

Questions? Check the main README.md for more details.

---

**Happy Delivery! 🍔🚁**
