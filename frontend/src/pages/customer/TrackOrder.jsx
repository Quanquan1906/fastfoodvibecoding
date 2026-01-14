/**
 * Customer Track Order - Real-time tracking with fake drone movement
 */
import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getOrder, updateOrderStatus, mockPayment } from "../../infrastructure/api/endpoints/orderApi";
import { connectOrderWebSocket, disconnectWebSocket } from "../../infrastructure/websocket/wsClient";
import DroneMap from "../../components/DroneMap";
import "./Customer.css";

function clamp01(x) {
  return Math.max(0, Math.min(1, x));
}

function CustomerTrackOrder() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const orderStatus = order?.status;
  const droneLat = order?.drone_lat;
  const droneLon = order?.drone_lon;
  const [loading, setLoading] = useState(true);
  const [paymentDone, setPaymentDone] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const [progress, setProgress] = useState(0);
  const [completing, setCompleting] = useState(false);
  const [deliveredMessage, setDeliveredMessage] = useState("");
  const [startPoint, setStartPoint] = useState(null);

  // Validate orderId on component mount
  useEffect(() => {
    if (!orderId || orderId === "undefined" || orderId.trim() === "") {
      setError("Invalid order ID. Please go back and try again.");
      setLoading(false);
    }
  }, [orderId]);

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

  useEffect(() => {
    if (orderStatus !== "DELIVERING") {
      return;
    }

    if (!startPoint && droneLat != null && droneLon != null) {
      setStartPoint({ lat: droneLat, lng: droneLon });
    }

    // Demo simulation: progress increases until arrival.
    const intervalId = setInterval(() => {
      setProgress((p) => {
        const next = Math.min(100, p + 5);
        return next;
      });
    }, 1000);

    return () => clearInterval(intervalId);
  }, [orderStatus, droneLat, droneLon, startPoint]);

  useEffect(() => {
    const shouldComplete = orderStatus === "DELIVERING" && progress >= 100;
    if (!shouldComplete || completing) return;

    const doComplete = async () => {
      setCompleting(true);
      try {
        const res = await updateOrderStatus(orderId, "COMPLETED");
        if (res?.success || res?.status === "COMPLETED") {
          setDeliveredMessage(res?.message || "Order delivered successfully");
          // Ensure UI updates even if websocket isn't available
          setOrder((prev) => (prev ? { ...prev, status: "COMPLETED" } : prev));
          await fetchOrder();
        } else {
          setDeliveredMessage("Order delivered successfully");
          setOrder((prev) => (prev ? { ...prev, status: "COMPLETED" } : prev));
        }
      } catch (error) {
        const detail = error?.response?.data?.detail;
        console.error("Failed to complete order:", error);
        setDeliveredMessage(detail || "Failed to mark order completed");
      } finally {
        setCompleting(false);
      }
    };

    doComplete();
  }, [progress, orderStatus, completing, orderId, fetchOrder]);

  const handleMockPayment = async () => {
    try {
      const response = await mockPayment(orderId);
      if (response?.success || response?.payment) {
        setPaymentDone(true);
        alert("✅ " + (response.payment?.message || "Payment successful"));
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

  const simulatedDronePosition = (() => {
    if (!startPoint) return null;
    if (order?.delivery_lat == null || order?.delivery_lon == null) return null;

    const t = clamp01(Number(progress) / 100);
    const lat = startPoint.lat + (order.delivery_lat - startPoint.lat) * t;
    const lng = startPoint.lng + (order.delivery_lon - startPoint.lng) * t;

    return { lat, lng };
  })();

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
            {order.delivery_address && (
              <h3>📍 Delivery Address: {order.delivery_address}</h3>
            )}
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
              {startPoint && order.delivery_lat != null && order.delivery_lon != null ? (
                <div style={{ marginBottom: 12 }}>
                  <DroneMap
                    startLat={startPoint.lat}
                    startLng={startPoint.lng}
                    endLat={order.delivery_lat}
                    endLng={order.delivery_lon}
                    progress={progress}
                  />
                </div>
              ) : null}
              <p>
                Latitude: {simulatedDronePosition ? simulatedDronePosition.lat.toFixed(6) : "—"}
              </p>
              <p>
                Longitude: {simulatedDronePosition ? simulatedDronePosition.lng.toFixed(6) : "—"}
              </p>
              <p>Destination: {order.delivery_lat?.toFixed(6)}, {order.delivery_lon?.toFixed(6)}</p>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${Math.min(100, progress)}%` }}
                >
                  {progress >= 100 ? "Arrived" : `Moving... ${progress}%`}
                </div>
              </div>
            </div>
          )}

          {order.status === "COMPLETED" && startPoint && (
            <div style={{ marginTop: 16 }}>
              <DroneMap
                startLat={startPoint.lat}
                startLng={startPoint.lng}
                endLat={order.delivery_lat}
                endLng={order.delivery_lon}
                progress={100}
              />
            </div>
          )}

          {order.status === "COMPLETED" && (
            <div className="completed-message">
              <h3>✅ Order Completed!</h3>
              <p>{deliveredMessage || "Order delivered successfully"}</p>
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
