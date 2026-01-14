/**
 * Login Page - Simple role-based authentication
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../infrastructure/api/endpoints/authApi";
import "./Login.css";

function Login() {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("CUSTOMER");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!username.trim()) {
      alert("Please enter a username");
      return;
    }

    setLoading(true);
    try {
      const response = await login(username, role);

      if (response) {
        const user = response.user || response;
        localStorage.setItem("user", JSON.stringify(user));

        // Redirect based on role
        const normalizedRole = (user.role || "").toUpperCase();

        if (normalizedRole === "CUSTOMER") {
          navigate("/customer/home");
        } else if (normalizedRole === "RESTAURANT") {
          if (!user.restaurant_id) {
            throw new Error("Missing restaurant_id for Restaurant login");
          }
          navigate(`/restaurant/dashboard/${user.restaurant_id}`);
        } else if (normalizedRole === "ADMIN") {
          navigate("/admin/dashboard");
        } else {
          throw new Error(`Unknown role: ${user.role}`);
        }
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      alert("❌ " + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>🍔 FastFood Delivery</h1>
        <p className="subtitle">Demo - Drone Food Delivery System</p>

        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your username"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Role:</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            disabled={loading}
          >
            <option value="CUSTOMER">🧑‍🍳 Customer</option>
            <option value="RESTAURANT">🏪 Restaurant</option>
            <option value="ADMIN">🛡️ Admin</option>
          </select>
        </div>

        <button onClick={handleLogin} disabled={loading} className="login-btn">
          {loading ? "⏳ Logging in..." : "✅ Login"}
        </button>

        <div className="demo-info">
          <p><strong>Demo Credentials:</strong></p>
          <p>• Username: any username</p>
          <p>• No password required</p>
          <p>• Choose your role and login</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
