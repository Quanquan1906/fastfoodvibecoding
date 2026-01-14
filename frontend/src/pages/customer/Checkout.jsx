/**
 * Customer Checkout - View Menu & Create Order
 */
import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getRestaurant, getMenuItems } from "../../infrastructure/api/endpoints/restaurantApi";
import { createOrder } from "../../infrastructure/api/endpoints/orderApi";
import "./Customer.css";

function CustomerCheckout() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const fetchRestaurantAndMenu = useCallback(async () => {
    try {
      setErrorMessage("");
      const [rest, menu] = await Promise.all([
        getRestaurant(restaurantId),
        getMenuItems(restaurantId),
      ]);
      setRestaurant(rest);
      setMenuItems(menu);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (status) setErrorMessage(detail || `Request failed (${status})`);
      else setErrorMessage("Network error: could not reach backend");
      setLoading(false);
    }
  }, [restaurantId]);

  useEffect(() => {
    fetchRestaurantAndMenu();
  }, [fetchRestaurantAndMenu]);

  const addToCart = (item) => {
    if (!user?.id) {
      alert("You have to sign in first");
      return;
    }
    const existingItem = cart.find((ci) => ci.menu_item_id === item.id);
    if (existingItem) {
      setCart(
        cart.map((ci) =>
          ci.menu_item_id === item.id
            ? { ...ci, quantity: ci.quantity + 1 }
            : ci
        )
      );
    } else {
      setCart([
        ...cart,
        {
          menu_item_id: item.id,
          name: item.name,
          price: Number(item.price),
          quantity: 1,
        },
      ]);
    }
  };

  const removeFromCart = (itemId) => {
    setCart(cart.filter((ci) => ci.menu_item_id !== itemId));
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + Number(item.price) * Number(item.quantity), 0);
  };

  const handlePlaceOrder = async () => {
    if (cart.length === 0) {
      alert("❌ Please add items to your cart");
      return;
    }

    if (!user?.id) {
      alert("❌ Missing customer id. Please log in again.");
      return;
    }

    if (!deliveryAddress.trim()) {
      alert("❌ Please enter a delivery address");
      return;
    }

    setOrdering(true);
    try {
      const total = Number(calculateTotal().toFixed(2));
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
        // Try multiple fields to extract order ID (order.id, id, order._id, _id)
        const orderId = response.order?.id || response.order?._id || response.id || response._id;
        
        // Validate orderId before navigation
        if (!orderId || orderId === "undefined") {
          alert("❌ Error: Order created but ID not returned. Please go back and check your orders.");
          return;
        }
        
        navigate(`/customer/track/${orderId}`);
      }
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (status === 422) {
        alert("❌ Validation error (422). Check required fields and types.");
        console.error("422 detail:", detail);
      } else {
        alert("❌ Error creating order: " + (detail || error.message));
      }
    } finally {
      setOrdering(false);
    }
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading...</p></div>;
  }

  return (
    <div className="page-container">
      <div className="header">
        <button onClick={() => navigate("/customer/home")} className="btn btn-back">
          ← Back
        </button>
        <h1>📋 {restaurant?.name}</h1>
      </div>

      <div className="checkout-container">
        <div className="menu-section">
          <h2>Menu Items</h2>
          {errorMessage ? <p className="empty-state">❌ {errorMessage}</p> : null}
          <div className="menu-grid">
            {menuItems.length === 0 ? (
              <p>No items available</p>
            ) : (
              menuItems.map((item) => (
                <div key={item.id} className="menu-item-card">
                  {item.image_url ? (
                    <img
                      className="menu-item-image"
                      src={item.image_url}
                      alt={item.name}
                      loading="lazy"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  ) : null}
                  <h4>{item.name}</h4>
                  <p>{item.description}</p>
                  <p className="price">💵 ${item.price.toFixed(2)}</p>
                  <button
                    onClick={() => addToCart(item)}
                    className="btn btn-primary btn-small"
                  >
                    ➕ Add to Cart
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="cart-section">
          <h2>🛒 Cart</h2>
          {cart.length === 0 ? (
            <p className="empty-state">Cart is empty</p>
          ) : (
            <>
              <div className="cart-items">
                {cart.map((item) => (
                  <div key={item.menu_item_id} className="cart-item">
                    <div>
                      <p className="item-name">{item.name}</p>
                      <p className="item-price">
                        ${item.price.toFixed(2)} x {item.quantity}
                      </p>
                    </div>
                    <button
                      onClick={() => removeFromCart(item.menu_item_id)}
                      className="btn btn-danger btn-small"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>

              <div className="cart-total">
                <h3>Total: ${calculateTotal().toFixed(2)}</h3>
              </div>

              <div className="address-input-container" style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>
                  📍 Delivery Address
                </label>
                <input
                  type="text"
                  placeholder="Enter your delivery address"
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  className="input-field"
                  style={{
                    width: "100%",
                    padding: "10px",
                    border: "1px solid #ddd",
                    borderRadius: "6px",
                    fontSize: "16px",
                  }}
                />
              </div>

              <button
                onClick={handlePlaceOrder}
                disabled={ordering}
                className="btn btn-primary btn-large"
              >
                {ordering ? "⏳ Placing Order..." : "✅ Place Order"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default CustomerCheckout;
