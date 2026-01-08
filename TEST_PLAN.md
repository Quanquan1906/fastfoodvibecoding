# 🧪 FastFood Demo - Test Plan & Scenarios

## Quick Test Checklist

Use this checklist to verify all features are working correctly.

---

## ✅ Pre-Test Setup

- [ ] MongoDB is running (`mongod`)
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] Browser opens to login page
- [ ] No console errors in browser or terminal

---

## Test Scenario 1: Simple Customer Order (5 min)

### Objective
Verify basic customer flow: browse → order → pay → track

### Steps

**Step 1: Login as Customer**
- [ ] Open http://localhost:3000
- [ ] Enter username: `customer1`
- [ ] Select role: `CUSTOMER`
- [ ] Click Login
- [ ] Should see "Browse Restaurants" page

**Step 2: Browse Restaurants**
- [ ] See list of restaurants (or empty if first time)
- [ ] Each restaurant card should show name, description, address
- [ ] Click "View Menu" on any restaurant
- [ ] Should navigate to checkout/menu page

**Step 3: View Menu & Add Items**
- [ ] See menu items on left side
- [ ] See empty cart on right side
- [ ] Click "➕ Add to Cart" on items
- [ ] Items appear in cart
- [ ] Click "➕ Add to Cart" again on same item
- [ ] Quantity increases

**Step 4: Place Order**
- [ ] Total price updates in cart
- [ ] Click "✅ Place Order"
- [ ] Should navigate to order tracking page

**Step 5: Mock Payment**
- [ ] See order status as "⏳ PENDING"
- [ ] Click "💳 Mock Payment (Always Succeeds)"
- [ ] Should see success message
- [ ] Status should change to "👨‍🍳 PREPARING"

**Step 6: Track Order**
- [ ] See order details and items
- [ ] See order timeline
- [ ] See drone tracking info once status is "DELIVERING"
- [ ] Drone latitude/longitude should update
- [ ] After ~40 seconds, status should be "✅ COMPLETED"

**Step 7: View Orders History**
- [ ] Click "📦 My Orders" in header
- [ ] Should see completed order in list
- [ ] Can click "Track" to view order again

**Result**: ✅ Customer can complete full order flow

---

## Test Scenario 2: Restaurant Operations (10 min)

### Objective
Verify restaurant management: menu management, order fulfillment

### Prerequisites
- First, use Admin to create a restaurant (see Scenario 4)

### Steps

**Step 1: Login as Restaurant Owner**
- [ ] Open new browser tab/window
- [ ] Login with role: `RESTAURANT`
- [ ] Should see Restaurant Dashboard

**Step 2: Add Menu Items**
- [ ] Click "🍽️ Menu" tab
- [ ] In "Add New Item" form:
  - [ ] Name: "Margherita Pizza"
  - [ ] Description: "Fresh pizza"
  - [ ] Price: "12.99"
  - [ ] Click "➕ Add Item"
- [ ] Should see "✅ Menu item added!"
- [ ] Item appears in "Current Menu" list
- [ ] Repeat with 2-3 more items

**Step 3: View Orders**
- [ ] Click "📋 Orders" tab
- [ ] Should be empty initially
- [ ] Have customer (in another tab) place order from this restaurant
- [ ] Refresh or wait for order to appear

**Step 4: Accept Order**
- [ ] See incoming order with status "PENDING"
- [ ] Click "✅ Accept"
- [ ] Order status should change to "PREPARING"
- [ ] Button should change to "📦 Ready"

**Step 5: Mark Ready**
- [ ] Click "📦 Ready"
- [ ] Status changes to "READY_FOR_PICKUP"
- [ ] Should show "⏳ Waiting for drone assignment..."

**Result**: ✅ Restaurant can manage menu and orders

---

## Test Scenario 3: Admin Multi-Tenancy (10 min)

### Objective
Verify admin can create restaurants and drones, manage entire system

### Steps

**Step 1: Login as Admin**
- [ ] Open new browser tab
- [ ] Login with role: `ADMIN`
- [ ] Should see Admin Dashboard with 4 tabs

**Step 2: Create Restaurants**
- [ ] Click "🏪 Restaurants" tab
- [ ] Fill in:
  - [ ] Name: "Pizza Palace"
  - [ ] Owner ID: `restaurant_owner_1`
  - [ ] Description: "Best pizza in town"
- [ ] Click "➕ Create"
- [ ] Should see "✅ Restaurant created!"
- [ ] Restaurant appears in list
- [ ] Repeat to create 2 restaurants total

**Step 3: Create Drones**
- [ ] Click "🚁 Drones" tab
- [ ] Fill in:
  - [ ] Name: "Drone-01"
  - [ ] Select Restaurant from dropdown
  - [ ] Click "➕ Create"
- [ ] Should see "✅ Drone created!"
- [ ] Drone appears in list
- [ ] Create 2-3 more drones (can assign to same or different restaurants)

**Step 4: View Users**
- [ ] Click "👥 Users" tab
- [ ] Should see table with username, role, restaurant
- [ ] Should see users created from Customer/Restaurant tests
- [ ] Admin users, restaurant users, customer users visible

**Step 5: View All Orders**
- [ ] Click "📋 All Orders" tab
- [ ] Should see orders created during other scenarios
- [ ] Each order shows status, total, items count
- [ ] Can see orders from different customers and restaurants

**Result**: ✅ Admin can manage entire system

---

## Test Scenario 4: Real-Time Drone Delivery (15 min)

### Objective
Verify fake drone movement simulation and real-time tracking

### Prerequisites
- Have Admin and Customer ready in separate tabs
- Have a restaurant created with drone assigned

### Steps

**Step 1: Prepare System**
- [ ] In Admin tab, create Restaurant and Drone (if not done)
- [ ] Note the drone ID and restaurant ID

**Step 2: Customer Orders**
- [ ] In Customer tab, order from the restaurant
- [ ] Complete mock payment
- [ ] Should see order tracking page

**Step 3: Restaurant Accepts**
- [ ] In Restaurant tab, accept the order
- [ ] Mark as "📦 Ready"

**Step 4: Admin Assigns Drone**
- [ ] In Admin tab (if you add this functionality):
  - [ ] Find pending order
  - [ ] Click "Assign Drone" button
  - [ ] Select drone from restaurant
  - [ ] Submit

**Note**: Currently, drone assignment would be done via API or Admin panel expansion

**Step 5: Watch Tracking**
- [ ] Go back to Customer tab
- [ ] On tracking page, wait for status to change to "DELIVERING"
- [ ] Watch the GPS coordinates update:
  - [ ] Latitude should increase by ~0.0005 every 2 seconds
  - [ ] Longitude should increase by ~0.0005 every 2 seconds
- [ ] See progress bar animating

**Step 6: Completion**
- [ ] After ~40 seconds, status should change to "✅ COMPLETED"
- [ ] Drone returns to IDLE status
- [ ] See completion message

**Result**: ✅ Fake drone movement and delivery simulation works

---

## Test Scenario 5: Multi-User Concurrent Access (15 min)

### Objective
Verify system handles multiple concurrent users and real-time updates

### Setup
- Open 4 browser windows/tabs:
  1. Customer 1
  2. Customer 2
  3. Restaurant
  4. Admin

### Steps

**Step 1: Setup Users**
- [ ] Tab 1: Login as `customer1`, role `CUSTOMER`
- [ ] Tab 2: Login as `customer2`, role `CUSTOMER`
- [ ] Tab 3: Login as `restaurant1`, role `RESTAURANT`
- [ ] Tab 4: Login as `admin1`, role `ADMIN`

**Step 2: Concurrent Orders**
- [ ] Tab 1 (Customer 1): Browse and order
- [ ] Tab 2 (Customer 2): Browse and order
- [ ] Both from same restaurant if possible
- [ ] Complete payments for both

**Step 3: Restaurant Receives Multiple**
- [ ] Tab 3 (Restaurant): Should see both orders
- [ ] Accept Customer 1's order
- [ ] Tab 1: Should see status change in real-time

**Step 4: Admin Monitors**
- [ ] Tab 4 (Admin): Go to "📋 All Orders" tab
- [ ] Should see both orders from both customers
- [ ] Should show current statuses

**Step 5: Concurrent Tracking**
- [ ] Tab 1 & 2: Both viewing order tracking
- [ ] Both should receive real-time updates
- [ ] Drone positions should update simultaneously

**Result**: ✅ System handles multiple concurrent users

---

## Test Scenario 6: Error Handling (5 min)

### Objective
Verify system handles errors gracefully

### Steps

**Step 1: Invalid Login**
- [ ] Open login page
- [ ] Leave username empty
- [ ] Click Login
- [ ] Should show error message

**Step 2: Missing Items**
- [ ] In Customer: Try to order without adding items
- [ ] Should show error or be prevented

**Step 3: Missing Fields**
- [ ] In Restaurant: Try to add menu item without price
- [ ] Should show error

**Step 4: Concurrent Payments**
- [ ] Order something, start payment
- [ ] Click payment button twice quickly
- [ ] Should handle gracefully, not duplicate

**Result**: ✅ System error handling works

---

## Performance Tests

### Response Times
- [ ] Login: < 1 second
- [ ] Browse restaurants: < 1 second
- [ ] Place order: < 2 seconds
- [ ] Payment: < 1 second
- [ ] WebSocket update: < 2 seconds

### Concurrent Connections
- [ ] 5 simultaneous users: No issues
- [ ] Multiple orders: No server errors
- [ ] Multiple WebSocket connections: All receive updates

---

## Browser Compatibility

Test on:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)

**Expected**: All features work identically

---

## Final Verification Checklist

### Customer Features
- [ ] ✅ Can login
- [ ] ✅ Can browse restaurants
- [ ] ✅ Can view menu
- [ ] ✅ Can add to cart
- [ ] ✅ Can place order
- [ ] ✅ Can make payment
- [ ] ✅ Can track order in real-time
- [ ] ✅ Can view order history

### Restaurant Features
- [ ] ✅ Can login
- [ ] ✅ Can add menu items
- [ ] ✅ Can view menu items
- [ ] ✅ Can receive orders
- [ ] ✅ Can accept orders
- [ ] ✅ Can mark orders ready
- [ ] ✅ Can see order status updates

### Admin Features
- [ ] ✅ Can login
- [ ] ✅ Can create restaurants
- [ ] ✅ Can view all restaurants
- [ ] ✅ Can create drones
- [ ] ✅ Can view all drones
- [ ] ✅ Can view all users
- [ ] ✅ Can view all orders
- [ ] ✅ Can manage multi-tenant system

### Technical Features
- [ ] ✅ WebSocket real-time updates
- [ ] ✅ Fake drone GPS movement
- [ ] ✅ Order status lifecycle
- [ ] ✅ Mock payment system
- [ ] ✅ Database persistence
- [ ] ✅ Concurrent user handling

---

## Known Limitations (by design)

- Single-page navigation (no page refresh needed)
- In-memory WebSocket connections (lost on server restart)
- No authentication persistence (demo only)
- Fake drone movement is simulated (not real GPS)
- Mock payment always succeeds
- Limited input validation (for demo simplicity)

---

## Bug Report Template

If you find issues, note:
1. **Steps to Reproduce**: What did you do?
2. **Expected Result**: What should happen?
3. **Actual Result**: What actually happened?
4. **Browser**: Chrome, Firefox, Safari?
5. **Screenshot**: If applicable
6. **Console Errors**: Any errors in browser console?

---

## 🎉 Test Complete!

If all checks pass, the FastFood Delivery System is working perfectly! 

---

**Happy Testing! 🧪**
