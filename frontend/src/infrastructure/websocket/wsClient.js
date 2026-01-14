/**
 * WebSocket client - infrastructure layer
 */
const WS_BASE_URL = process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8000';

export const connectOrderWebSocket = (orderId, handlers) => {
  const ws = new WebSocket(`${WS_BASE_URL}/ws/orders/${orderId}`);
  
  ws.onopen = () => {
    console.log(`✅ WebSocket connected for order ${orderId}`);
    if (handlers.onOpen) handlers.onOpen();
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (handlers.onMessage) handlers.onMessage(data);
  };
  
  ws.onerror = (error) => {
    console.error(`❌ WebSocket error for order ${orderId}:`, error);
    if (handlers.onError) handlers.onError(error);
  };
  
  ws.onclose = () => {
    console.log(`🔌 WebSocket disconnected for order ${orderId}`);
    if (handlers.onClose) handlers.onClose();
  };
  
  return ws;
};

export const disconnectWebSocket = (ws) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
};
