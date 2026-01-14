# Bug Fix: OrderId Becoming Undefined in Customer Tracking

## Problem Summary
The customer order tracking feature was failing with `orderId` becoming `undefined`:
- **Symptom**: URL shows `/customer/track/undefined`
- **API Call**: `GET /orders/undefined` returns 404
- **WebSocket**: `ws://localhost:8000/ws/orders/undefined` fails to connect
- **User Experience**: "Order not found" error message

## Root Cause Analysis

### Primary Issues Identified:

1. **Missing Input Validation in TrackOrder.jsx**
   - `useParams()` extracts orderId but no validation occurs before using it
   - `getOrder(orderId)` called even when orderId is undefined
   - WebSocket URL constructed with undefined orderId
   - No error state to distinguish "missing orderId" from "order not found"

2. **Missing Validation in Checkout.jsx**
   - Response structure parsing: `response.order?.id || response.id`
   - If both properties are undefined, orderId becomes undefined
   - Navigation proceeds with undefined orderId without validation

3. **Missing Validation in Orders.jsx**
   - `handleTrackOrder()` navigates without validating orderId
   - If orders list contains undefined IDs, navigation fails silently

4. **No Defensive Error Handling**
   - No guard clause before API/WebSocket calls
   - No user-friendly error message when orderId is invalid
   - No redirect logic for invalid orderId scenarios

## Code Changes Implemented

### Fix 1: TrackOrder.jsx - Add OrderId Validation

**Location**: `/frontend/src/pages/customer/TrackOrder.jsx`

**Changes Made**:

1. Added `error` state to track invalid orderId
```javascript
const [error, setError] = useState(null);
```

2. Added validation effect on component mount
```javascript
// Validate orderId on component mount
useEffect(() => {
  if (!orderId || orderId === "undefined" || orderId.trim() === "") {
    setError("Invalid order ID. Please go back and try again.");
    setLoading(false);
  }
}, [orderId]);
```

3. Added guard clause in `fetchOrder` callback
```javascript
const fetchOrder = useCallback(async () => {
  // Guard against invalid orderId
  if (!orderId || orderId === "undefined") {
    console.warn("Invalid orderId, skipping fetch");
    return;
  }
  
  try {
    const data = await getOrder(orderId);
    setOrder(data);
    if (data?.status === "COMPLETED") {
      setProgress(100);
      setDeliveredMessage("Order delivered successfully");
    }
    setLoading(false);
  } catch (error) {
    console.error("Error fetching order:", error);
    setError("Failed to load order. Please try again.");
    setLoading(false);
  }
}, [orderId]);
```

4. Added guard clause in `setupWebSocket` callback
```javascript
const setupWebSocket = useCallback(() => {
  // Guard against invalid orderId
  if (!orderId || orderId === "undefined") {
    console.warn("Invalid orderId, skipping WebSocket setup");
    return;
  }

  const wsUrl = `ws://localhost:8000/ws/orders/${orderId}`;
  const wsConnection = new WebSocket(wsUrl);

  wsConnection.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setOrder(data);
  };

  wsConnection.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  wsConnection.onclose = () => {
    console.log("WebSocket closed");
  };

  wsRef.current = wsConnection;
}, [orderId]);
```

5. Updated main useEffect to conditionally call fetch/setup
```javascript
useEffect(() => {
  // Only fetch and setup WebSocket if orderId is valid
  if (orderId && orderId !== "undefined") {
    fetchOrder();
    setupWebSocket();
  }

  return () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };
}, [fetchOrder, setupWebSocket]);
```

6. Added error render before loading check
```javascript
if (error) {
  return (
    <div className="page-container">
      <p>❌ {error}</p>
      <button onClick={() => navigate("/customer/orders")} className="btn btn-primary">
        Back to Orders
      </button>
    </div>
  );
}

if (loading) {
  return <div className="page-container"><p>⏳ Loading order...</p></div>;
}
```

### Fix 2: Checkout.jsx - Validate OrderId Before Navigation

**Location**: `/frontend/src/pages/customer/Checkout.jsx` (lines ~100-130)

**Changes Made**:

Added validation after response parsing:
```javascript
const response = await createOrder({
  customer_id: user.id,
  restaurant_id: restaurantId,
  items: cart.map((ci) => ({
    menu_item_id: String(ci.menu_item_id),
    name: String(ci.name),
    price: Number(ci.price),
    quantity: Number(ci.quantity),
  })),
  total_price: total,
  delivery_address: deliveryAddress.trim(),
});

if (response) {
  const orderId = response.order?.id || response.id;
  
  // Validate orderId before navigation
  if (!orderId || orderId === "undefined") {
    alert("❌ Error: Order created but ID not returned. Please go back and check your orders.");
    return;
  }
  
  navigate(`/customer/track/${orderId}`);
}
```

### Fix 3: Orders.jsx - Validate OrderId Before Navigation

**Location**: `/frontend/src/pages/customer/Orders.jsx` (lines ~35)

**Changes Made**:

Updated `handleTrackOrder` function:
```javascript
const handleTrackOrder = (orderId) => {
  // Validate orderId before navigation
  if (!orderId || orderId === "undefined" || orderId.trim() === "") {
    alert("❌ Invalid order ID. Cannot track this order.");
    return;
  }
  navigate(`/customer/track/${orderId}`);
};
```

## API Response Structure Verification

**Backend Endpoint**: `POST /orders` (order_router.py, line 33)

**Response Format**:
```json
{
  "success": true,
  "order": {
    "_id": "ObjectId",
    "id": "string",
    "status": "PENDING",
    "customer_id": "string",
    "restaurant_id": "string",
    "items": [...],
    "total_price": 50.00,
    "delivery_address": "123 Main St",
    "drone_id": null,
    "drone_lat": null,
    "drone_lon": null,
    "created_at": "timestamp"
  }
}
```

**Frontend Parser** (orderApi.js):
```javascript
export const createOrder = async (orderData) => {
  const response = await apiClient.post('/orders', orderData);
  return response.data;  // Returns: { success: true, order: {...} }
};
```

**Response Extraction** (Checkout.jsx):
```javascript
const orderId = response.order?.id || response.id;
// This correctly extracts from the nested structure
```

## Testing Checklist

- [ ] Test 1: Create new order in Checkout page
  - Expected: orderId extracted correctly from response
  - Expected: Validation passes, navigation succeeds
  - Expected: URL shows `/customer/track/{valid_id}`

- [ ] Test 2: Navigate to TrackOrder page
  - Expected: orderId loaded from URL params
  - Expected: API call to `GET /orders/{id}` succeeds
  - Expected: WebSocket connects to `ws://localhost:8000/ws/orders/{id}`
  - Expected: Order data loads and displays

- [ ] Test 3: Manually navigate with invalid orderId
  - URL: `http://localhost:3000/customer/track/invalid`
  - Expected: Error message displayed
  - Expected: "Back to Orders" button available

- [ ] Test 4: Manually navigate with undefined orderId
  - URL: `http://localhost:3000/customer/track/undefined`
  - Expected: Error message displayed
  - Expected: "Back to Orders" button available

- [ ] Test 5: View existing orders
  - Navigate to Orders page
  - Click "Track" button on any order
  - Expected: Validation passes, navigation succeeds
  - Expected: Order tracking page loads

- [ ] Test 6: WebSocket connection
  - Create and track new order
  - Check browser DevTools → Network → WS
  - Expected: WebSocket connection to valid URL succeeds
  - Expected: Status message updates in real-time

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `frontend/src/pages/customer/TrackOrder.jsx` | Added orderId validation, error state, guard clauses | 15-90, 180-195 |
| `frontend/src/pages/customer/Checkout.jsx` | Added orderId validation before navigation | 115-125 |
| `frontend/src/pages/customer/Orders.jsx` | Added orderId validation in handleTrackOrder | 35-42 |

## Impact Analysis

### What This Fixes
✅ Prevents navigation with undefined orderId
✅ Prevents API calls with undefined orderId  
✅ Prevents WebSocket connections with undefined orderId
✅ Provides user-friendly error messages
✅ Allows users to navigate back safely
✅ Distinguishes "missing orderId" from "order not found"

### What This Doesn't Change
- Backend API structure or response format
- Order creation logic
- Order status management
- WebSocket message handling
- Drone tracking logic
- Payment processing

### Performance Impact
- **Minimal**: One additional validation effect on component mount
- **Benefit**: Prevents unnecessary API/WebSocket calls with invalid parameters

### User Experience Improvement
- **Before**: Generic "Order not found" message with no recovery
- **After**: Clear error message with navigation to Orders page

## Error States Handled

| Scenario | Before | After |
|----------|--------|-------|
| orderId is undefined | Navigates to `/customer/track/undefined` | Shows error, no navigation |
| orderId is string "undefined" | API call returns 404 | Shows error before API call |
| orderId is empty string | WebSocket URL malformed | Shows error before WebSocket |
| API response missing id | undefined navigation | Alert and return, no navigation |
| WebSocket fails | Generic error in console | Logged as warning, graceful degradation |

## Deployment Notes

1. **Frontend Build**: Run `npm run build` to create production build
2. **Testing Environment**: No backend changes required
3. **Backward Compatibility**: All changes are additive (no breaking changes)
4. **Browser Compatibility**: Uses standard JavaScript/React APIs

## Related Issues

- May resolve issues where users see blank tracking pages
- May resolve WebSocket connection timeout errors
- May resolve 404 errors on order tracking API calls

## Future Improvements

1. Add logging/analytics for invalid orderId attempts
2. Add automatic redirect to Orders page after timeout
3. Add retry mechanism for failed WebSocket connections
4. Add order ID copy-to-clipboard functionality
5. Add QR code for order tracking link
