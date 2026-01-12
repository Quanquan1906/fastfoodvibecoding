/**
 * Restaurant Dashboard
 */
import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../services/api";
import "./Restaurant.css";

function RestaurantDashboard() {
  const navigate = useNavigate();
  const params = useParams();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [restaurant, setRestaurant] = useState(null);
  const [activeTab, setActiveTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [addingMenuItem, setAddingMenuItem] = useState(false);
  const [assigningOrderId, setAssigningOrderId] = useState(null);
  const [availableDrones, setAvailableDrones] = useState([]);
  const [selectedDroneId, setSelectedDroneId] = useState("");
  const [loadingDrones, setLoadingDrones] = useState(false);
  const [newItem, setNewItem] = useState({
    name: "",
    description: "",
    price: "",
  });
  const [newItemImage, setNewItemImage] = useState(null);

  const effectiveRestaurantId = params.restaurantId || user.restaurant_id;

  useEffect(() => {
    if (!user || user.role !== "RESTAURANT") {
      navigate("/login", { replace: true });
      return;
    }

    if (!effectiveRestaurantId) {
      setLoading(false);
      return;
    }

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveRestaurantId]);

  const fetchData = async () => {
    try {
      setErrorMessage("");
      
      // Fetch restaurant details with ownership check
      const restaurantRes = await api.get(
        `/restaurants/${effectiveRestaurantId}`,
        { params: { username: user.username, role: user.role } }
      );
      
      const restaurantData = restaurantRes.data;
      
      // Verify ownership with case-insensitive and trimmed comparison
      const ownerUsername = restaurantData.owner_username?.trim().toLowerCase();
      const userUsername = user.username?.trim().toLowerCase();
      
      console.log("[OWNERSHIP CHECK] Owner:", ownerUsername);
      console.log("[OWNERSHIP CHECK] User:", userUsername);
      
      // Only block if role is RESTAURANT and usernames don't match
      if (user.role === "RESTAURANT" && ownerUsername && ownerUsername !== userUsername) {
        console.log("[OWNERSHIP CHECK] DENIED - Usernames do not match");
        alert("❌ You are not the owner of this restaurant.");
        navigate("/", { replace: true });
        return;
      }
      
      console.log("[OWNERSHIP CHECK] ALLOWED");
      setRestaurant(restaurantData);
      
      const [ordersRes, menuRes] = await Promise.all([
        api.get(`/restaurant/${effectiveRestaurantId}/orders`),
        api.get(`/restaurants/${effectiveRestaurantId}/menu`),
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

    if (!newItemImage) {
      alert("❌ Please select an image");
      return;
    }

    try {
      setErrorMessage("");
      setAddingMenuItem(true);

      const formData = new FormData();
      formData.append("restaurant_id", user.restaurant_id);
      formData.append("name", newItem.name);
      formData.append("description", newItem.description || "");
      formData.append("price", String(parseFloat(newItem.price)));
      formData.append("image", newItemImage);

      // Do NOT set Content-Type manually; axios will add the correct boundary.
      await api.post("/restaurant/menu", formData);

      setNewItem({ name: "", description: "", price: "" });
      setNewItemImage(null);
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
    } finally {
      setAddingMenuItem(false);
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
      await api.post(
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

  const startAssignDrone = async (orderId) => {
    setAssigningOrderId(orderId);
    setSelectedDroneId("");
    setAvailableDrones([]);
    setLoadingDrones(true);
    setErrorMessage("");

    try {
      const res = await api.get(`/restaurant/${user.restaurant_id}/drones`);
      setAvailableDrones(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (status === 400 || status === 404 || status === 409) {
        setErrorMessage(detail || `Request failed (${status})`);
      } else {
        setErrorMessage("Failed to fetch drones");
      }
      setAssigningOrderId(null);
    } finally {
      setLoadingDrones(false);
    }
  };

  const confirmAssignDrone = async (orderId) => {
    if (!selectedDroneId) {
      alert("❌ Please select a drone");
      return;
    }

    try {
      setErrorMessage("");
      await api.post(`/orders/${orderId}/assign-drone`, { drone_id: selectedDroneId });
      setAssigningOrderId(null);
      setSelectedDroneId("");
      setAvailableDrones([]);
      await fetchData();
      alert("✅ Drone assigned!");
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (status === 400 || status === 404 || status === 409) {
        alert(`❌ ${detail || `Request failed (${status})`}`);
      } else {
        alert("❌ Failed to assign drone");
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading...</p></div>;
  }

  if (!effectiveRestaurantId) {
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
          Please contact an admin to create a restaurant and assign your username as the owner.
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
                        <div>
                          {assigningOrderId === order.id ? (
                            <div>
                              {loadingDrones ? (
                                <p className="info">⏳ Loading drones...</p>
                              ) : availableDrones.length === 0 ? (
                                <p className="info">No available drones</p>
                              ) : (
                                <>
                                  <select
                                    value={selectedDroneId}
                                    onChange={(e) => setSelectedDroneId(e.target.value)}
                                  >
                                    <option value="">Select a drone</option>
                                    {availableDrones.map((d) => (
                                      <option key={d.id} value={d.id}>
                                        {d.name} ({d.status})
                                      </option>
                                    ))}
                                  </select>
                                  <div style={{ marginTop: 8 }}>
                                    <button
                                      onClick={() => confirmAssignDrone(order.id)}
                                      className="btn btn-primary"
                                      disabled={!selectedDroneId}
                                    >
                                      🚁 Assign
                                    </button>
                                    <button
                                      onClick={() => setAssigningOrderId(null)}
                                      className="btn btn-danger"
                                      style={{ marginLeft: 8 }}
                                    >
                                      ✕
                                    </button>
                                  </div>
                                </>
                              )}
                            </div>
                          ) : (
                            <>
                              <p className="info">⏳ Waiting for drone assignment...</p>
                              <button
                                onClick={() => startAssignDrone(order.id)}
                                className="btn btn-primary"
                              >
                                🚁 Assign Drone
                              </button>
                            </>
                          )}
                        </div>
                      )}
                      {order.status === "DELIVERING" && (
                        <p className="info">
                          🚁 Delivering{order.drone_name ? ` with ${order.drone_name}` : ""}...
                        </p>
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
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setNewItemImage(e.target.files?.[0] || null)}
              />
              <button onClick={handleAddMenuItem} className="btn btn-primary" disabled={addingMenuItem}>
                {addingMenuItem ? "⏳ Uploading..." : "➕ Add Item"}
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
                      {item.image_url ? (
                        <img
                          className="menu-list-item-image"
                          src={item.image_url}
                          alt={item.name}
                          loading="lazy"
                          onError={(e) => {
                            e.currentTarget.style.display = "none";
                          }}
                        />
                      ) : null}
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
