/**
 * Order context - moved from infrastructure/context
 */
import React, { createContext, useState, useCallback } from 'react';
import * as orderApi from '../../infrastructure/api/endpoints/orderApi';

export const OrderContext = createContext();

export const OrderProvider = ({ children }) => {
  const [orders, setOrders] = useState([]);
  const [currentOrder, setCurrentOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCustomerOrders = useCallback(async (customerId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderApi.getCustomerOrders(customerId);
      setOrders(response || []);
      return response;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch orders';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchOrder = useCallback(async (orderId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderApi.getOrder(orderId);
      setCurrentOrder(response);
      return response;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch order';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createOrder = useCallback(async (orderData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderApi.createOrder(orderData);
      if (response.success) {
        setCurrentOrder(response.order);
        return response.order;
      } else {
        throw new Error(response.message || 'Failed to create order');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create order';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateOrderStatus = useCallback(async (orderId, status) => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderApi.mockPayment(orderId);
      if (response.success && response.payment) {
        setCurrentOrder(response.payment.order);
        return response.payment;
      }
      throw new Error('Failed to update order');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update order';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    orders,
    currentOrder,
    loading,
    error,
    fetchCustomerOrders,
    fetchOrder,
    createOrder,
    updateOrderStatus,
    setCurrentOrder
  };

  return (
    <OrderContext.Provider value={value}>
      {children}
    </OrderContext.Provider>
  );
};
