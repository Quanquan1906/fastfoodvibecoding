/**
 * Auth context - moved from infrastructure/context
 */
import React, { createContext, useState, useEffect } from 'react';
import * as authApi from '../../infrastructure/api/endpoints/authApi';
import * as localStorage from '../../infrastructure/storage/localStorage';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is logged in on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(storedUser);
    }
    setLoading(false);
  }, []);

  const login = async (username, role) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authApi.login(username, role);
      
      if (response.success) {
        setUser(response.user);
        localStorage.setItem('user', response.user);
        return response.user;
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
