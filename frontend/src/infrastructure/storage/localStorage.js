/**
 * Storage module - local storage wrapper
 */
export const setItem = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

export const getItem = (key) => {
  const item = localStorage.getItem(key);
  return item ? JSON.parse(item) : null;
};

export const removeItem = (key) => {
  localStorage.removeItem(key);
};

export const clearAll = () => {
  localStorage.clear();
};
