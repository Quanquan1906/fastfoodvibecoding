import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Pages
import Login from './pages/Login';
import CustomerHome from './pages/customer/Home';
import CustomerCheckout from './pages/customer/Checkout';
import CustomerTrackOrder from './pages/customer/TrackOrder';
import CustomerOrders from './pages/customer/Orders';
import RestaurantDashboard from './pages/restaurant/Dashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

function App() {
  return (
    <Router>
      <Routes>
        {/* Auth */}
        <Route path="/" element={<Login />} />

        {/* Customer Routes */}
        <Route path="/customer/home" element={<CustomerHome />} />
        <Route path="/customer/checkout/:restaurantId" element={<CustomerCheckout />} />
        <Route path="/customer/track/:orderId" element={<CustomerTrackOrder />} />
        <Route path="/customer/orders" element={<CustomerOrders />} />

        {/* Restaurant Routes */}
        <Route path="/restaurant/dashboard" element={<RestaurantDashboard />} />

        {/* Admin Routes */}
        <Route path="/admin/dashboard" element={<AdminDashboard />} />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
