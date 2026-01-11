/**
 * Admin Dashboard
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Admin.css";

function AdminDashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [activeTab, setActiveTab] = useState("restaurants");
  const [restaurants, setRestaurants] = useState([]);
  const [drones, setDrones] = useState([]);
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newRestaurant, setNewRestaurant] = useState({
    name: "",
    owner_id: "",
    description: "",
  });
  const [newDrone, setNewDrone] = useState({
    name: "",
    restaurant_id: "",
  });

  useEffect(() => {
    if (!user || user.role !== "ADMIN") {
      navigate("/login", { replace: true });
      return;
    }
    fetchAllData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAllData = async () => {
    try {
      const [restRes, droneRes, usersRes, ordersRes] = await Promise.all([
        api.get("/admin/restaurants"),
        api.get("/admin/drones"),
        api.get("/admin/users"),
        api.get("/admin/orders"),
      ]);
      setRestaurants(restRes.data);
      setDrones(droneRes.data);
      setUsers(usersRes.data);
      setOrders(ordersRes.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  const handleCreateRestaurant = async () => {
    if (!newRestaurant.name || !newRestaurant.owner_id) {
      alert("❌ Please fill in name and owner ID");
      return;
    }

    try {
      await api.post("/admin/restaurants", newRestaurant);
      setNewRestaurant({ name: "", owner_id: "", description: "" });
      await fetchAllData();
      alert("✅ Restaurant created!");
    } catch (error) {
      alert("❌ Error: " + error.message);
    }
  };

  const handleCreateDrone = async () => {
    if (!newDrone.name || !newDrone.restaurant_id) {
      alert("❌ Please fill in name and select restaurant");
      return;
    }

    try {
      await api.post("/admin/drones", newDrone);
      setNewDrone({ name: "", restaurant_id: "" });
      await fetchAllData();
      alert("✅ Drone created!");
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

  return (
    <div className="page-container">
      <div className="header">
        <h1>🛡️ Admin Dashboard</h1>
        <button onClick={handleLogout} className="btn btn-logout">
          🚪 Logout
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === "restaurants" ? "active" : ""}`}
          onClick={() => setActiveTab("restaurants")}
        >
          🏪 Restaurants
        </button>
        <button
          className={`tab ${activeTab === "drones" ? "active" : ""}`}
          onClick={() => setActiveTab("drones")}
        >
          🚁 Drones
        </button>
        <button
          className={`tab ${activeTab === "users" ? "active" : ""}`}
          onClick={() => setActiveTab("users")}
        >
          👥 Users
        </button>
        <button
          className={`tab ${activeTab === "orders" ? "active" : ""}`}
          onClick={() => setActiveTab("orders")}
        >
          📋 All Orders
        </button>
      </div>

      <div className="content">
        {activeTab === "restaurants" && (
          <div>
            <h2>Restaurant Management</h2>

            <div className="form-section">
              <h3>Create Restaurant</h3>
              <input
                type="text"
                placeholder="Restaurant name"
                value={newRestaurant.name}
                onChange={(e) => setNewRestaurant({ ...newRestaurant, name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Owner ID"
                value={newRestaurant.owner_id}
                onChange={(e) => setNewRestaurant({ ...newRestaurant, owner_id: e.target.value })}
              />
              <input
                type="text"
                placeholder="Description"
                value={newRestaurant.description}
                onChange={(e) => setNewRestaurant({ ...newRestaurant, description: e.target.value })}
              />
              <button onClick={handleCreateRestaurant} className="btn btn-primary">
                ➕ Create
              </button>
            </div>

            <div className="items-list">
              <h3>All Restaurants</h3>
              {restaurants.length === 0 ? (
                <p className="empty-state">No restaurants</p>
              ) : (
                <div className="grid">
                  {restaurants.map((rest) => (
                    <div key={rest.id} className="item-card">
                      <h4>{rest.name}</h4>
                      <p>Owner: {rest.owner_id?.substring(0, 8)}</p>
                      <p>{rest.description}</p>
                      <p className="id">ID: {rest.id?.substring(0, 12)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "drones" && (
          <div>
            <h2>Drone Management</h2>

            <div className="form-section">
              <h3>Create Drone</h3>
              <input
                type="text"
                placeholder="Drone name"
                value={newDrone.name}
                onChange={(e) => setNewDrone({ ...newDrone, name: e.target.value })}
              />
              <select
                value={newDrone.restaurant_id}
                onChange={(e) => setNewDrone({ ...newDrone, restaurant_id: e.target.value })}
              >
                <option value="">Select Restaurant</option>
                {restaurants.map((rest) => (
                  <option key={rest.id} value={rest.id}>
                    {rest.name}
                  </option>
                ))}
              </select>
              <button onClick={handleCreateDrone} className="btn btn-primary">
                ➕ Create
              </button>
            </div>

            <div className="items-list">
              <h3>All Drones</h3>
              {drones.length === 0 ? (
                <p className="empty-state">No drones</p>
              ) : (
                <div className="grid">
                  {drones.map((drone) => (
                    <div key={drone.id} className="item-card">
                      <h4>{drone.name}</h4>
                      <p>Status: {drone.status}</p>
                      <p>Location: ({drone.latitude?.toFixed(4)}, {drone.longitude?.toFixed(4)})</p>
                      <p className="id">ID: {drone.id?.substring(0, 12)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "users" && (
          <div>
            <h2>User Management</h2>
            <div className="items-list">
              {users.length === 0 ? (
                <p className="empty-state">No users</p>
              ) : (
                <div className="table-view">
                  <table>
                    <thead>
                      <tr>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Restaurant</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td>{user.username}</td>
                          <td>
                            <span className={`badge badge-${user.role.toLowerCase()}`}>
                              {user.role}
                            </span>
                          </td>
                          <td>{user.restaurant_id?.substring(0, 8) || "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "orders" && (
          <div>
            <h2>System Orders Overview</h2>
            <div className="items-list">
              {orders.length === 0 ? (
                <p className="empty-state">No orders</p>
              ) : (
                <div className="grid">
                  {orders.map((order) => (
                    <div key={order.id} className="item-card">
                      <h4>Order #{order.id?.substring(0, 8)}</h4>
                      <p>Status: <span style={{ fontWeight: "bold", color: order.status === "COMPLETED" ? "green" : "orange" }}>{order.status}</span></p>
                      <p>Total: ${order.total?.toFixed(2)}</p>
                      <p>Items: {order.items?.length}</p>
                      <p className="id">Customer: {order.customer_id?.substring(0, 8)}</p>
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

export default AdminDashboard;
