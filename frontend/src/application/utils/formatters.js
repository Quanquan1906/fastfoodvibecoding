/**
 * Application utilities
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US');
};

export const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('en-US');
};

export const calculateDeliveryTime = (createdAt) => {
  const created = new Date(createdAt);
  const now = new Date();
  const minutes = Math.floor((now - created) / 1000 / 60);
  return `${minutes} min ago`;
};
