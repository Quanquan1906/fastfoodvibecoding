/**
 * Application validation services - business logic for validation
 */

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUsername = (username) => {
  return username && username.length >= 3 && username.length <= 30;
};

export const validateDeliveryAddress = (address) => {
  return address && address.trim().length >= 5;
};

export const validatePhoneNumber = (phone) => {
  const phoneRegex = /^[\d\s\-\+\(\)]+$/;
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
};

export const validateRestaurantName = (name) => {
  return name && name.trim().length >= 3 && name.trim().length <= 100;
};

export const validateMenuItemPrice = (price) => {
  const numPrice = parseFloat(price);
  return !isNaN(numPrice) && numPrice > 0 && numPrice <= 10000;
};
