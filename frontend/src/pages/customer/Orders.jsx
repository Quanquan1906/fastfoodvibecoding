/**
 * View Customer Orders
 */
import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Customer.css";

function CustomerOrders() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = useCallback(async () => {
    try {
      const response = await api.get(`/customer/${user.id}/orders`);
      setOrders(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching orders:", error);
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleTrackOrder = (orderId) => {
    navigate(`/customer/track/${orderId}`);
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading orders...</p></div>;
  }

  return (
    <div className="page-container">
      <div className="header">
        <button onClick={() => navigate("/customer/home")} className="btn btn-back">
          ← Back
        </button>
        <h1>📦 My Orders</h1>
      </div>

      <div className="content">
        {orders.length === 0 ? (
          <p className="empty-state">No orders yet. Start ordering! 🍔</p>
        ) : (
          <div className="orders-list">
            {orders.map((order) => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <h3>Order #{order.id?.substring(0, 8)}</h3>
                  <span className="status" style={{ color: order.status === "COMPLETED" ? "green" : "orange" }}>
                    {order.status}
                  </span>
                </div>
                <p>Total: ${order.total?.toFixed(2)}</p>
                <p>Items: {order.items?.length}</p>
                <button
                  onClick={() => handleTrackOrder(order.id)}
                  className="btn btn-primary btn-small"
                >
                  Track
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CustomerOrders;
