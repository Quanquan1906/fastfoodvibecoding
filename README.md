# 🍔 FastFood Delivery System - Full Stack Demo

A working demonstration of a drone food delivery system built with React (Frontend) and FastAPI (Backend).

## ✨ Features

### 🧑‍🍳 Customer Role
- ✅ Browse restaurants
- ✅ View restaurant menus
- ✅ Create orders
- ✅ Mock payment (always succeeds)
- ✅ Real-time order tracking with fake drone movement
- ✅ View order history

### 🏪 Restaurant Role
- ✅ Manage menu items (create, view)
- ✅ View incoming orders
- ✅ Accept orders
- ✅ Update order status
- ✅ Ready orders for pickup

### 🛡️ Admin Role
- ✅ Create restaurants (multi-tenant)
- ✅ Create and manage drones
- ✅ View all users
- ✅ View system-wide orders
- ✅ System management dashboard

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **MongoDB** - NoSQL database with Motor async driver
- **WebSocket** - Real-time order tracking
- **Pydantic** - Data validation

### Frontend
- **React 19** - UI library
- **React Router v6** - Navigation
- **Axios** - HTTP client
- **CSS3** - Styling

## 📋 Prerequisites

- **MongoDB** running locally on `mongodb://localhost:27017`
- **Python 3.9+** for backend
- **Node.js 18+** for frontend
- **npm** package manager

## 🚀 Quick Start

### 1. Start MongoDB

If you don't have MongoDB installed, follow the [official installation guide](https://docs.mongodb.com/manual/installation/).

```bash
# On Windows (if installed via chocolatey or installer)
mongod

# On macOS (if installed via homebrew)
brew services start mongodb-community

# On Linux
sudo systemctl start mongod
```

Verify MongoDB is running:
```bash
mongo --version
```

### 2. Setup Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open at: `http://localhost:3000`

## 📝 Demo Credentials

The system uses **simple, role-based login** (NO password required):

1. **Customer Demo**
   - Username: `john_customer` (or any username)
   - Role: `CUSTOMER`

2. **Restaurant Demo**
   - Username: `restaurant_owner` (or any username)
   - Role: `RESTAURANT`

3. **Admin Demo**
   - Username: `admin_user` (or any username)
   - Role: `ADMIN`

## 🎯 Demo Walkthrough

### As a Customer:
1. Login with username and select "CUSTOMER"
2. Browse available restaurants
3. Click "View Menu" on a restaurant
4. Add items to cart
5. Place order
6. Click "Mock Payment" (always succeeds)
7. Watch the fake drone movement in real-time
8. Order completes automatically after simulated delivery

### As a Restaurant Owner:
1. Login with username and select "RESTAURANT"
2. View incoming orders in the "Orders" tab
3. Click "Accept" to accept a pending order
4. Click "Ready" when order is prepared (PREPARING → READY_FOR_PICKUP)
5. Wait for admin to assign a drone

### As an Admin:
1. Login with username and select "ADMIN"
2. **Restaurants Tab**: Create new restaurants and view all
3. **Drones Tab**: Create drones and assign to restaurants
4. **Users Tab**: View all system users
5. **Orders Tab**: Monitor all orders system-wide
6. Manage the complete system

## 📊 System Flow

```
Customer Orders Food
    ↓
Payment (Mock - Always Succeeds)
    ↓
Restaurant Receives Order (Status: PENDING)
    ↓
Restaurant Accepts (Status: PREPARING)
    ↓
Restaurant Marks Ready (Status: READY_FOR_PICKUP)
    ↓
Admin Assigns Drone + Starts Delivery (Status: DELIVERING)
    ↓
Fake Drone Movement (GPS coordinates simulated)
    ↓
Order Completes (Status: COMPLETED)
```

## 🎬 API Endpoints Summary

### Auth
- `POST /login` - Simple login

### Customer
- `GET /restaurants` - List all restaurants
- `GET /restaurants/{id}` - Get restaurant details
- `GET /restaurants/{id}/menu` - Get menu items
- `POST /orders` - Create order
- `GET /orders/{id}` - Get order details
- `POST /payments/mock/{id}` - Mock payment
- `WS /ws/orders/{id}` - Real-time order tracking

### Restaurant
- `POST /restaurant/menu` - Add menu item
- `PUT /restaurant/menu/{id}` - Update menu item
- `DELETE /restaurant/menu/{id}` - Delete menu item
- `GET /restaurant/{id}/orders` - Get restaurant's orders
- `POST /restaurant/orders/{id}/accept` - Accept order
- `POST /restaurant/orders/{id}/status` - Update status
- `POST /restaurant/orders/{id}/assign-drone` - Assign drone

### Admin
- `POST /admin/restaurants` - Create restaurant
- `GET /admin/restaurants` - List restaurants
- `POST /admin/drones` - Create drone
- `GET /admin/drones` - List drones
- `GET /admin/users` - List users
- `GET /admin/orders` - List all orders

## 🧪 Testing the System

### Test Customer Flow:
```
1. Login as customer
2. Browse restaurants
3. Add items to cart
4. Place order
5. Pay (mock)
6. Watch drone tracking
7. Order completes automatically
```

### Test Restaurant Flow:
```
1. Admin creates restaurant
2. Admin creates drone
3. Customer places order
4. Restaurant sees order
5. Restaurant accepts order
6. Restaurant marks ready
7. Admin assigns drone to order
8. Restaurant watches delivery
```

### Test Multiple Users:
- Open multiple browser tabs
- Login as different roles
- Test concurrent operations
- See real-time updates via WebSocket

## 📁 Project Structure

```
FastFood/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── core/
│   │   │   └── database.py         # MongoDB connection
│   │   ├── models/                 # Pydantic models
│   │   │   ├── user.py
│   │   │   ├── restaurant.py
│   │   │   ├── menu_item.py
│   │   │   ├── order.py
│   │   │   └── drone.py
│   │   ├── services/               # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── order_service.py
│   │   │   ├── drone_service.py
│   │   │   └── payment_service.py
│   │   ├── api/
│   │   │   └── routes.py           # All endpoints
│   │   └── websocket/
│   │       └── manager.py          # WebSocket manager
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── customer/
    │   │   │   ├── Home.jsx
    │   │   │   ├── Checkout.jsx
    │   │   │   ├── TrackOrder.jsx
    │   │   │   ├── Orders.jsx
    │   │   │   └── Customer.css
    │   │   ├── restaurant/
    │   │   │   ├── Dashboard.jsx
    │   │   │   └── Restaurant.css
    │   │   └── admin/
    │   │       ├── AdminDashboard.jsx
    │   │       └── Admin.css
    │   ├── services/
    │   │   └── api.js              # Axios client
    │   ├── App.js
    │   └── App.css
    ├── package.json
    └── public/
```

## ⚙️ Key Features Explained

### Simple Authentication
- No password hashing
- No JWT tokens
- Just username + role selection
- Auto-create user on first login

### Mock Payment
- Always succeeds instantly
- Transitions order to PREPARING
- No real payment gateway

### Fake Drone Movement
- Simulates 20 steps of movement
- Moves coordinates by 0.0005 every 2 seconds
- Broadcasts updates via WebSocket
- Auto-completes order after delivery

### Real-time Tracking
- WebSocket connection per order
- Auto-updates every 2 seconds
- Shows fake GPS coordinates
- Live status updates

### Multi-Tenant System
- Restaurants are isolated
- Admin can create multiple restaurants
- Each restaurant has own menu, orders, drones
- Users linked to restaurants

## 🔐 Security Note

⚠️ **This is a DEMO application, NOT production-ready!**
- No authentication security
- No input validation beyond Pydantic
- No rate limiting
- Mock payment only
- For demonstration purposes only

## 🛠️ Troubleshooting

### MongoDB Connection Error
```
Error: Connection refused
Solution: Make sure MongoDB is running on localhost:27017
```

### Port Already in Use (8000)
```
Solution: Kill process on port 8000 or use different port
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### CORS Errors
```
Solution: Backend CORS is already configured to accept all origins
Make sure frontend is on http://localhost:3000
```

### WebSocket Connection Failed
```
Solution: Make sure backend is running and WebSocket is enabled
Check browser console for connection details
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [MongoDB Documentation](https://docs.mongodb.com)
- [React Router Documentation](https://reactrouter.com)

## 🎉 Summary

This is a complete, working demo of a food delivery system with:
- ✅ 3 user roles with different capabilities
- ✅ Real-time WebSocket tracking
- ✅ Fake drone movement simulation
- ✅ Mock payment system
- ✅ Multi-tenant restaurant support
- ✅ Simple, no-auth login
- ✅ Fully functional UI
- ✅ Easy to run and understand

Perfect for demos, learning, or as a starting point for real applications!

---

**Happy coding! 🚀** 🍔🚁
