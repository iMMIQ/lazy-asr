import { useState, useEffect, useRef, useCallback } from 'react';
import type { WSMessage, WSStatusData } from '../types';

/**
 * WebSocket connection status
 */
export type WSConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * Configuration options for useWebSocket hook
 */
export interface UseWebSocketOptions {
  /** WebSocket server URL (defaults to ws://localhost:8000/api/v1/ws) */
  baseUrl?: string;
  /** Enable automatic reconnection (default: true) */
  autoReconnect?: boolean;
  /** Maximum number of reconnection attempts (default: 10) */
  maxReconnectAttempts?: number;
  /** Delay between reconnection attempts in ms (default: 3000) */
  reconnectDelay?: number;
  /** Enable ping/pong heartbeat (default: true) */
  enableHeartbeat?: boolean;
  /** Interval for sending ping messages in ms (default: 30000) */
  heartbeatInterval?: number;
  /** Enable infinite reconnection attempts (default: false) */
  infiniteReconnect?: boolean;
}

/**
 * Return type for useWebSocket hook
 */
export interface UseWebSocketReturn {
  /** Current WebSocket connection status */
  status: WSConnectionStatus;
  /** Whether the WebSocket is connected */
  connected: boolean;
  /** Last received message */
  lastMessage: WSMessage | null;
  /** Last received status data */
  lastStatus: WSStatusData | null;
  /** Connection error if any */
  error: string | null;
  /** Function to send a message through the WebSocket */
  sendMessage: (message: Record<string, unknown>) => void;
  /** Function to manually disconnect */
  disconnect: () => void;
  /** Function to manually reconnect */
  reconnect: () => void;
}

const DEFAULT_WS_URL = 'ws://localhost:8000/api/v1/ws';

/**
 * Custom hook for managing WebSocket connections
 *
 * This hook provides a complete WebSocket client implementation with:
 * - Automatic connection management
 * - Auto-reconnection with configurable backoff
 * - Message parsing and type safety
 * - Connection status tracking
 * - Heartbeat/ping-pong support
 *
 * @param scanId - The scan ID to connect to
 * @param options - Configuration options for the WebSocket connection
 * @returns WebSocket connection state and control functions
 *
 * @example
 * ```tsx
 * const { connected, lastStatus, status } = useWebSocket('scan-123', {
 *   autoReconnect: true,
 *   maxReconnectAttempts: 10
 * });
 *
 * if (connected) {
 *   console.log('Current progress:', lastStatus?.progress);
 * }
 * ```
 */
export function useWebSocket(
  scanId: string | null,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    baseUrl = DEFAULT_WS_URL,
    autoReconnect = true,
    maxReconnectAttempts = 10,
    reconnectDelay = 3000,
    enableHeartbeat = true,
    heartbeatInterval = 30000,
    infiniteReconnect = false,
  } = options;

  const [status, setStatus] = useState<WSConnectionStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [lastStatus, setLastStatus] = useState<WSStatusData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    cleanup();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('disconnected');
    reconnectAttemptsRef.current = 0;
  }, [cleanup]);

  const connect = useCallback(() => {
    if (!scanId) {
      setStatus('disconnected');
      return;
    }

    // Don't connect if already connected or connecting
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING ||
                          wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }

    cleanup();
    setStatus('connecting');
    setError(null);

    try {
      const wsUrl = `${baseUrl}/scan/${scanId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.addEventListener('open', () => {
        setStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Setup heartbeat if enabled
        if (enableHeartbeat) {
          heartbeatTimeoutRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }));
            }
          }, heartbeatInterval);
        }
      });

      ws.addEventListener('message', (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Parse status messages
          if (message.type === 'status' && message.data) {
            setLastStatus(message.data as WSStatusData);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      });

      ws.addEventListener('error', (event) => {
        console.error('WebSocket error:', event);
        setStatus('error');
        setError('WebSocket connection error');
      });

      ws.addEventListener('close', (event) => {
        setStatus('disconnected');
        cleanup();

        // Attempt reconnection if enabled and not intentionally closed
        if (autoReconnect && !event.wasClean && (infiniteReconnect || reconnectAttemptsRef.current < maxReconnectAttempts)) {
          reconnectAttemptsRef.current++;
          const delay = reconnectDelay * reconnectAttemptsRef.current; // Exponential backoff

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      });
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Failed to create WebSocket connection');
    }
  }, [scanId, baseUrl, autoReconnect, maxReconnectAttempts, reconnectDelay, enableHeartbeat, heartbeatInterval, infiniteReconnect, cleanup]);

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('Cannot send message: WebSocket is not connected');
    }
  }, []);

  // Connect on mount and when scanId changes
  useEffect(() => {
    if (scanId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [scanId]); // Only reconnect when scanId changes

  return {
    status,
    connected: status === 'connected',
    lastMessage,
    lastStatus,
    error,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}

export default useWebSocket;
