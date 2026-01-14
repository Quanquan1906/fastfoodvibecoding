/**
 * Authentication API endpoints
 */
import apiClient from '../apiClient';

export const login = async (username, role) => {
  const response = await apiClient.post('/login', { username, role });
  return response.data;
};

export const getUser = async (userId) => {
  const response = await apiClient.get(`/users/${userId}`);
  return response.data;
};

export const getAllUsers = async () => {
  const response = await apiClient.get('/admin/users');
  return response.data;
};
