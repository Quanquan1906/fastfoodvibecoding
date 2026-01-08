/**
 * Customer Home - Browse Restaurants
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Customer.css";

function CustomerHome() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    fetchRestaurants();
  }, []);

  const fetchRestaurants = async () => {
    try {
      const response = await api.get("/restaurants");
      setRestaurants(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching restaurants:", error);
      setLoading(false);
    }
  };

  const handleSelectRestaurant = (restaurantId) => {
    navigate(`/customer/checkout/${restaurantId}`);
  };

  const handleViewOrders = () => {
    navigate("/customer/orders");
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading restaurants...</p></div>;
  }

  return (
    <div className="page-container">
      <div className="header">
        <h1>🍔 FastFood Delivery</h1>
        <div className="header-actions">
          <button onClick={handleViewOrders} className="btn btn-secondary">
            📦 My Orders
          </button>
          <button onClick={handleLogout} className="btn btn-logout">
            🚪 Logout
          </button>
        </div>
      </div>

      <div className="content">
        <h2>Browse Restaurants</h2>

        {restaurants.length === 0 ? (
          <p className="empty-state">No restaurants available yet.</p>
        ) : (
          <div className="restaurants-grid">
            {restaurants.map((restaurant) => (
              <div key={restaurant.id} className="restaurant-card">
                <div className="restaurant-header">
                  <h3>{restaurant.name}</h3>
                </div>
                <p className="restaurant-description">{restaurant.description || "No description"}</p>
                <p className="restaurant-address">📍 {restaurant.address || "Address not provided"}</p>
                <p className="restaurant-phone">📞 {restaurant.phone || "Phone not provided"}</p>
                <button
                  onClick={() => handleSelectRestaurant(restaurant.id)}
                  className="btn btn-primary"
                >
                  👀 View Menu
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CustomerHome;
