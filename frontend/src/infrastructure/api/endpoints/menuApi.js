/**
 * Menu API endpoints
 */
import apiClient from '../apiClient';

export const createMenuItem = async (formData) => {
  const response = await apiClient.post('/restaurant/menu', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const updateMenuItem = async (itemId, itemData) => {
  const response = await apiClient.put(`/restaurant/menu/${itemId}`, itemData);
  return response.data;
};

export const deleteMenuItem = async (itemId) => {
  const response = await apiClient.delete(`/restaurant/menu/${itemId}`);
  return response.data;
};
