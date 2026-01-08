/**
 * Customer Track Order - Real-time tracking with fake drone movement
 */
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Customer.css";

function CustomerTrackOrder() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paymentDone, setPaymentDone] = useState(false);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    fetchOrder();
    setupWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      const response = await api.get(`/orders/${orderId}`);
      setOrder(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching order:", error);
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/orders/${orderId}`;
    const wsConnection = new WebSocket(wsUrl);

    wsConnection.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setOrder(data);
    };

    wsConnection.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    setWs(wsConnection);
  };

  const handleMockPayment = async () => {
    try {
      const response = await api.post(`/payments/mock/${orderId}`);
      if (response.data.success) {
        setPaymentDone(true);
        alert("✅ " + response.data.payment.message);
        // Refresh order status
        await fetchOrder();
      }
    } catch (error) {
      alert("❌ Payment failed: " + error.message);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      PENDING: "#ffa500",
      PREPARING: "#4169e1",
      READY_FOR_PICKUP: "#32cd32",
      DELIVERING: "#ff6347",
      COMPLETED: "#228b22",
    };
    return colors[status] || "#666";
  };

  const getStatusEmoji = (status) => {
    const emojis = {
      PENDING: "⏳",
      PREPARING: "👨‍🍳",
      READY_FOR_PICKUP: "📦",
      DELIVERING: "🚁",
      COMPLETED: "✅",
    };
    return emojis[status] || "❓";
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading order...</p></div>;
  }

  if (!order) {
    return (
      <div className="page-container">
        <p>❌ Order not found</p>
        <button onClick={() => navigate("/customer/home")} className="btn btn-primary">
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="header">
        <button onClick={() => navigate("/customer/home")} className="btn btn-back">
          ← Home
        </button>
        <h1>📍 Track Your Order</h1>
      </div>

      <div className="track-container">
        <div className="order-info">
          <h2>Order #{order.id?.substring(0, 8)}</h2>
          <p className="status-badge" style={{ backgroundColor: getStatusColor(order.status) }}>
            {getStatusEmoji(order.status)} {order.status}
          </p>

          <div className="order-details">
            <h3>Items:</h3>
            <ul>
              {order.items?.map((item, idx) => (
                <li key={idx}>
                  {item.quantity}x {item.name} - ${(item.price * item.quantity).toFixed(2)}
                </li>
              ))}
            </ul>
            <h3>Total: ${order.total?.toFixed(2)}</h3>
          </div>

          {order.status === "PENDING" && !paymentDone && (
            <button
              onClick={handleMockPayment}
              className="btn btn-primary btn-large"
            >
              💳 Mock Payment (Always Succeeds)
            </button>
          )}

          {order.status === "DELIVERING" && order.drone_id && (
            <div className="drone-tracking">
              <h3>🚁 Drone Tracking</h3>
              <p>Latitude: {order.drone_lat?.toFixed(6)}</p>
              <p>Longitude: {order.drone_lon?.toFixed(6)}</p>
              <p>Destination: {order.delivery_lat?.toFixed(6)}, {order.delivery_lon?.toFixed(6)}</p>
              <div className="progress-bar">
                <div className="progress-fill">Moving...</div>
              </div>
            </div>
          )}

          {order.status === "COMPLETED" && (
            <div className="completed-message">
              <h3>✅ Order Completed!</h3>
              <p>Thank you for your order! 🎉</p>
              <button
                onClick={() => navigate("/customer/home")}
                className="btn btn-primary"
              >
                Order Another
              </button>
            </div>
          )}
        </div>

        <div className="timeline">
          <h3>Order Timeline</h3>
          <div className="timeline-item" style={{ opacity: order.status !== "PENDING" ? 1 : 0.5 }}>
            ⏳ Pending
          </div>
          <div className="timeline-item" style={{ opacity: order.status !== "PENDING" && order.status !== "READY_FOR_PICKUP" ? 1 : 0.5 }}>
            👨‍🍳 Preparing
          </div>
          <div className="timeline-item" style={{ opacity: order.status === "DELIVERING" || order.status === "COMPLETED" ? 1 : 0.5 }}>
            🚁 Delivering
          </div>
          <div className="timeline-item" style={{ opacity: order.status === "COMPLETED" ? 1 : 0.5 }}>
            ✅ Completed
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomerTrackOrder;
