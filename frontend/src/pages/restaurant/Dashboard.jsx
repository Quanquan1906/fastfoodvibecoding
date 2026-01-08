/**
 * Restaurant Dashboard
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Restaurant.css";

function RestaurantDashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [activeTab, setActiveTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [newItem, setNewItem] = useState({
    name: "",
    description: "",
    price: "",
  });

  useEffect(() => {
    if (!user || user.role !== "RESTAURANT") {
      navigate("/", { replace: true });
      return;
    }

    if (!user.restaurant_id) {
      setLoading(false);
      return;
    }

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.restaurant_id]);

  const fetchData = async () => {
    try {
      setErrorMessage("");
      const [ordersRes, menuRes] = await Promise.all([
        api.get(`/restaurant/${user.restaurant_id}/orders`),
        api.get(`/restaurants/${user.restaurant_id}/menu`),
      ]);

      setOrders(Array.isArray(ordersRes.data) ? ordersRes.data : []);
      setMenuItems(Array.isArray(menuRes.data) ? menuRes.data : []);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);

      if (error?.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail;

        if (status === 400) setErrorMessage(detail || "Bad request (400)");
        else if (status === 404) setErrorMessage(detail || "Not found (404)");
        else if (status >= 500) setErrorMessage("Backend error (500). Please try again.");
        else setErrorMessage(detail || `Request failed (${status})`);
      } else {
        setErrorMessage("Network error: could not reach backend");
      }

      setLoading(false);
    }
  };

  const handleAddMenuItem = async () => {
    if (!newItem.name || !newItem.price) {
      alert("❌ Please fill in name and price");
      return;
    }

    try {
      setErrorMessage("");
      await api.post("/restaurant/menu", {
        restaurant_id: user.restaurant_id,
        name: newItem.name,
        description: newItem.description,
        price: parseFloat(newItem.price),
        available: true,
      });

      setNewItem({ name: "", description: "", price: "" });
      await fetchData();
      alert("✅ Menu item added!");
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (status === 400 || status === 404) {
        alert(`❌ ${detail || `Request failed (${status})`}`);
      } else {
        alert("❌ Error adding item: " + (detail || error.message));
      }
    }
  };

  const handleAcceptOrder = async (orderId) => {
    try {
      await api.post(`/restaurant/orders/${orderId}/accept`);
      await fetchData();
      alert("✅ Order accepted!");
    } catch (error) {
      alert("❌ Error: " + error.message);
    }
  };

  const handleUpdateStatus = async (orderId, status) => {
    try {
      const response = await api.post(
        `/restaurant/orders/${orderId}/status`,
        null,
        { params: { status } }
      );
      await fetchData();
      alert(`✅ Status updated to ${status}`);
    } catch (error) {
      alert("❌ Error: " + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading...</p></div>;
  }

  if (!user.restaurant_id) {
    return (
      <div className="page-container">
        <div className="header">
          <h1>🏪 Restaurant Dashboard</h1>
          <button onClick={handleLogout} className="btn btn-logout">
            🚪 Logout
          </button>
        </div>
        <p className="empty-state">
          This restaurant account isn’t linked to a restaurant yet.
        </p>
        <p className="empty-state">
          Please log out and log in again (it will auto-create one), or create a restaurant via the Admin dashboard.
        </p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="header">
        <h1>🏪 Restaurant Dashboard</h1>
        <button onClick={handleLogout} className="btn btn-logout">
          🚪 Logout
        </button>
      </div>

      {errorMessage ? <p className="empty-state">❌ {errorMessage}</p> : null}

      <div className="tabs">
        <button
          className={`tab ${activeTab === "orders" ? "active" : ""}`}
          onClick={() => setActiveTab("orders")}
        >
          📋 Orders
        </button>
        <button
          className={`tab ${activeTab === "menu" ? "active" : ""}`}
          onClick={() => setActiveTab("menu")}
        >
          🍽️ Menu
        </button>
      </div>

      <div className="content">
        {activeTab === "orders" ? (
          <div>
            <h2>Incoming Orders</h2>
            {orders.length === 0 ? (
              <p className="empty-state">No orders yet</p>
            ) : (
              <div className="orders-table">
                {orders.map((order) => (
                  <div key={order.id} className="order-row">
                    <div>
                      <h4>Order #{order.id?.substring(0, 8)}</h4>
                      <p className="status">{order.status}</p>
                      <p>Total: ${order.total?.toFixed(2)}</p>
                      <p>Items: {order.items?.length}</p>
                    </div>
                    <div className="actions">
                      {order.status === "PENDING" && (
                        <button
                          onClick={() => handleAcceptOrder(order.id)}
                          className="btn btn-success"
                        >
                          ✅ Accept
                        </button>
                      )}
                      {order.status === "PREPARING" && (
                        <button
                          onClick={() => handleUpdateStatus(order.id, "READY_FOR_PICKUP")}
                          className="btn btn-primary"
                        >
                          📦 Ready
                        </button>
                      )}
                      {order.status === "READY_FOR_PICKUP" && (
                        <p className="info">⏳ Waiting for drone assignment...</p>
                      )}
                      {order.status === "DELIVERING" && (
                        <p className="info">🚁 On delivery...</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            <h2>Manage Menu</h2>

            <div className="add-item-form">
              <h3>Add New Item</h3>
              <input
                type="text"
                placeholder="Item name"
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Description"
                value={newItem.description}
                onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
              />
              <input
                type="number"
                placeholder="Price"
                step="0.01"
                value={newItem.price}
                onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
              />
              <button onClick={handleAddMenuItem} className="btn btn-primary">
                ➕ Add Item
              </button>
            </div>

            <div className="menu-list">
              <h3>Current Menu</h3>
              {menuItems.length === 0 ? (
                <p className="empty-state">No items yet</p>
              ) : (
                <div className="menu-items">
                  {menuItems.map((item) => (
                    <div key={item.id} className="menu-list-item">
                      <div>
                        <h4>{item.name}</h4>
                        <p>{item.description}</p>
                        <p className="price">${item.price?.toFixed(2)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RestaurantDashboard;
