/**
 * Application services - business logic without API calls
 */

export const calculateTotalPrice = (items) => {
  return items.reduce((total, item) => total + (item.price * item.quantity), 0);
};

export const validateOrderItems = (items) => {
  if (!Array.isArray(items) || items.length === 0) {
    return { valid: false, error: 'Order must have at least one item' };
  }
  
  for (const item of items) {
    if (!item.menu_item_id || !item.name || !item.price || !item.quantity) {
      return { valid: false, error: 'Invalid item data' };
    }
    if (item.quantity < 1) {
      return { valid: false, error: 'Item quantity must be at least 1' };
    }
    if (item.price < 0) {
      return { valid: false, error: 'Item price cannot be negative' };
    }
  }
  
  return { valid: true };
};

export const formatOrderStatus = (status) => {
  const statusMap = {
    PENDING: 'Pending',
    PREPARING: 'Preparing',
    READY_FOR_PICKUP: 'Ready for Pickup',
    DELIVERING: 'Delivering',
    COMPLETED: 'Completed'
  };
  return statusMap[status] || status;
};

export const isOrderDelivering = (order) => {
  return order && order.status === 'DELIVERING';
};

export const isOrderCompleted = (order) => {
  return order && order.status === 'COMPLETED';
};
