# OrderId Undefined Bug - Exact Code Changes

## File 1: frontend/src/pages/customer/TrackOrder.jsx

### Change 1: Add error state (line ~27)
```javascript
// ADDED:
const [error, setError] = useState(null);
```

### Change 2: Add validation useEffect (after line ~27, before fetchOrder)
```javascript
// ADDED:
// Validate orderId on component mount
useEffect(() => {
  if (!orderId || orderId === "undefined" || orderId.trim() === "") {
    setError("Invalid order ID. Please go back and try again.");
    setLoading(false);
  }
}, [orderId]);
```

### Change 3: Update fetchOrder callback (line ~38-48)
```javascript
// BEFORE:
const fetchOrder = useCallback(async () => {
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
    setLoading(false);
  }
}, [orderId]);

// AFTER:
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

### Change 4: Update setupWebSocket callback (line ~50-65)
```javascript
// BEFORE:
const setupWebSocket = useCallback(() => {
  const wsUrl = `ws://localhost:8000/ws/orders/${orderId}`;
  const wsConnection = new WebSocket(wsUrl);

  wsConnection.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setOrder(data);
  };

  wsConnection.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  wsRef.current = wsConnection;
}, [orderId]);

// AFTER:
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

### Change 5: Update main useEffect (line ~68-82)
```javascript
// BEFORE:
useEffect(() => {
  fetchOrder();
  setupWebSocket();

  return () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };
}, [fetchOrder, setupWebSocket]);

// AFTER:
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

### Change 6: Add error render before loading check (line ~190-205)
```javascript
// ADDED BEFORE existing if (loading) check:
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

---

## File 2: frontend/src/pages/customer/Checkout.jsx

### Change: Add orderId validation before navigation (line ~110-130)

```javascript
// BEFORE:
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
  navigate(`/customer/track/${orderId}`);
}

// AFTER:
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

---

## File 3: frontend/src/pages/customer/Orders.jsx

### Change: Update handleTrackOrder function (line ~35-42)

```javascript
// BEFORE:
const handleTrackOrder = (orderId) => {
  navigate(`/customer/track/${orderId}`);
};

// AFTER:
const handleTrackOrder = (orderId) => {
  // Validate orderId before navigation
  if (!orderId || orderId === "undefined" || orderId.trim() === "") {
    alert("❌ Invalid order ID. Cannot track this order.");
    return;
  }
  navigate(`/customer/track/${orderId}`);
};
```

---

## Summary of Changes

| File | Type | Purpose |
|------|------|---------|
| TrackOrder.jsx | 6 changes | Add validation before API/WebSocket, render error state |
| Checkout.jsx | 1 change | Validate orderId before navigation |
| Orders.jsx | 1 change | Validate orderId before navigation |

**Total Lines Added**: ~80 lines
**Total Lines Modified**: 3 sections
**Total Files Changed**: 3
**Breaking Changes**: None ✅

---

## Testing Each Change

### Test TrackOrder.jsx changes:
```javascript
// Test 1: Valid orderId
// Navigate to /customer/track/abc123
// Expected: Fetch and WebSocket both execute

// Test 2: Invalid orderId
// Navigate to /customer/track/undefined
// Expected: Error message shown, no API/WebSocket calls

// Test 3: Empty orderId
// Edit URL to /customer/track/
// Expected: Error message shown, back button works
```

### Test Checkout.jsx changes:
```javascript
// Test 1: Response with valid order.id
// Expected: Navigate to track page successfully

// Test 2: Response missing both order.id and id
// Expected: Alert shown, no navigation

// Test 3: Response with only id field
// Expected: Navigate to track page successfully
```

### Test Orders.jsx changes:
```javascript
// Test 1: Click track on valid order
// Expected: Navigate to track page successfully

// Test 2: Orders list has null/undefined id
// Expected: Alert shown, no navigation
```

---

## Rollback Instructions

If needed to revert, simply restore the original versions of:
1. `frontend/src/pages/customer/TrackOrder.jsx`
2. `frontend/src/pages/customer/Checkout.jsx`
3. `frontend/src/pages/customer/Orders.jsx`

No backend changes were made, so no rollback needed there.
