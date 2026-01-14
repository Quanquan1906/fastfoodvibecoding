/**
 * Customer Home - Browse Restaurants
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getRestaurants } from "../../infrastructure/api/endpoints/restaurantApi";
import "./Customer.css";

function CustomerHome() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    const onStorage = () => {
      try {
        const raw = localStorage.getItem("user");
        setUser(raw ? JSON.parse(raw) : null);
      } catch {
        setUser(null);
      }
    };

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  useEffect(() => {
    fetchRestaurants(currentPage);
  }, [currentPage]);

  const fetchRestaurants = async (page) => {
    try {
      setLoading(true);
      const data = await getRestaurants(page, 10);
      setRestaurants(data.data || []);
      setTotalPages(data.totalPages || 1);
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
    if (!user?.id) {
      navigate("/login");
      return;
    }
    navigate("/customer/orders");
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
    navigate("/");
  };

  const handleSignIn = () => {
    navigate("/login");
  };

  if (loading) {
    return <div className="page-container"><p>⏳ Loading restaurants...</p></div>;
  }

  return (
    <div className="page-container">
      <div className="header">
        <h1>🍔 FastFood Delivery</h1>
        <div className="header-actions">
          {!user?.id ? (
            <button onClick={handleSignIn} className="btn btn-primary">
              Sign In
            </button>
          ) : (
            <>
              {user?.role === "CUSTOMER" ? (
                <button onClick={handleViewOrders} className="btn btn-secondary">
                  📦 My Orders
                </button>
              ) : null}
              <button onClick={handleLogout} className="btn btn-logout">
                🚪 Logout
              </button>
            </>
          )}
        </div>
      </div>

      <div className="content">
        <h2>Browse Restaurants</h2>

        {restaurants.length === 0 ? (
          <p className="empty-state">No restaurants available yet.</p>
        ) : (
          <>
            <div className="restaurants-grid">
              {restaurants.map((restaurant) => (
                <div key={restaurant.id} className="restaurant-card">
                  {restaurant.image_url ? (
                    <img
                      className="restaurant-card-image"
                      src={restaurant.image_url}
                      alt={restaurant.name}
                      loading="lazy"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  ) : null}
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

            {totalPages > 1 && (
              <div className="pagination-controls" style={{ marginTop: "24px", textAlign: "center" }}>
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="btn btn-secondary"
                  style={{ marginRight: "12px" }}
                >
                  ← Previous
                </button>
                <span style={{ marginRight: "12px", fontSize: "16px", fontWeight: "bold" }}>
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default CustomerHome;
