/**
 * useWebSocket hook - WebSocket connection management
 */
import { useEffect, useRef } from 'react';
import { connectOrderWebSocket, disconnectWebSocket } from '../../infrastructure/websocket/wsClient';

export const useWebSocket = (orderId, handlers = {}) => {
  const wsRef = useRef(null);

  useEffect(() => {
    if (!orderId) return;

    wsRef.current = connectOrderWebSocket(orderId, handlers);

    return () => {
      disconnectWebSocket(wsRef.current);
    };
  }, [orderId, handlers]);

  return wsRef.current;
};
