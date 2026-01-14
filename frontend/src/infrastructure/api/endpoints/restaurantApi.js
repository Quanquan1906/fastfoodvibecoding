/**
 * Restaurant API endpoints
 */
import apiClient from '../apiClient';

export const getRestaurants = async (page = 1, limit = 6) => {
  const response = await apiClient.get('/restaurants', {
    params: { page, limit }
  });
  return response.data;
};

export const getRestaurant = async (restaurantId) => {
  const response = await apiClient.get(`/restaurants/${restaurantId}`);
  return response.data;
};

export const getMenuItems = async (restaurantId) => {
  const response = await apiClient.get(`/restaurants/${restaurantId}/menu`);
  return response.data;
};

export const getRestaurantOrders = async (restaurantId) => {
  const response = await apiClient.get(`/restaurant/${restaurantId}/orders`);
  return response.data;
};

export const getRestaurantDrones = async (restaurantId) => {
  const response = await apiClient.get(`/restaurant/${restaurantId}/drones`);
  return response.data;
};

export const acceptOrder = async (orderId) => {
  const response = await apiClient.post(`/restaurant/orders/${orderId}/accept`);
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await apiClient.post(`/restaurant/orders/${orderId}/status`, null, {
    params: { status }
  });
  return response.data;
};

export const createMenuItem = async (restaurantId, formData) => {
  const response = await apiClient.post('/restaurant/menu', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const updateRestaurant = async (restaurantId, formData) => {
  const response = await apiClient.put(`/restaurants/${restaurantId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const createRestaurant = async (formData) => {
  const response = await apiClient.post('/admin/restaurants', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getAllRestaurants = async () => {
  const response = await apiClient.get('/admin/restaurants');
  return response.data;
};
