/**
 * Order API endpoints
 */
import apiClient from '../apiClient';

export const createOrder = async (orderData) => {
  const response = await apiClient.post('/orders', orderData);
  return response.data;
};

export const getOrder = async (orderId) => {
  const response = await apiClient.get(`/orders/${orderId}`);
  return response.data;
};

export const getCustomerOrders = async (customerId) => {
  const response = await apiClient.get(`/customer/${customerId}/orders`);
  return response.data;
};

export const completeOrder = async (orderId) => {
  const response = await apiClient.post(`/orders/${orderId}/complete`);
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await apiClient.post(`/restaurant/orders/${orderId}/status`, { status });
  return response.data;
};

export const assignDrone = async (orderId, droneId) => {
  const response = await apiClient.post(`/orders/${orderId}/assign-drone`, { drone_id: droneId });
  return response.data;
};

export const mockPayment = async (orderId) => {
  const response = await apiClient.post(`/payments/mock/${orderId}`);
  return response.data;
};

export const getAllOrders = async () => {
  const response = await apiClient.get('/admin/orders');
  return response.data;
};

export const acceptOrder = async (orderId) => {
  const response = await apiClient.post(`/restaurant/orders/${orderId}/accept`);
  return response.data;
};

export const getRestaurantOrders = async (restaurantId) => {
  const response = await apiClient.get(`/restaurant/${restaurantId}/orders`);
  return response.data;
};
