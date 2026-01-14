/**
 * Drone API endpoints
 */
import apiClient from '../apiClient';

export const createDrone = async (formData) => {
  const response = await apiClient.post('/admin/drones', formData);
  return response.data;
};

export const getAllDrones = async () => {
  const response = await apiClient.get('/admin/drones');
  return response.data;
};

export const getRestaurantDrones = async (restaurantId) => {
  const response = await apiClient.get(`/admin/drones/restaurant/${restaurantId}`);
  return response.data;
};

export const getAvailableDrones = async (restaurantId) => {
  const response = await apiClient.get(`/restaurant/${restaurantId}/drones`);
  return response.data;
};

export const assignDrone = async (orderId, droneId) => {
  const response = await apiClient.post(`/orders/${orderId}/assign-drone`, { drone_id: droneId });
  return response.data;
};

export const assignDroneToRestaurant = async (droneId, restaurantId) => {
  const response = await apiClient.post('/admin/assign-drone', {
    drone_id: droneId,
    restaurant_id: restaurantId
  });
  return response.data;
};
