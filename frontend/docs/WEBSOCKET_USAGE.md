# WebSocket Usage Guide

## Overview

This application uses WebSocket as the exclusive real-time communication method.
All scan status updates and ASR processing progress are delivered via WebSocket.

## Connection

### Scan Updates
```typescript
const { connected, lastStatus, status } = useWebSocket(scanId, {
  autoReconnect: true,
  maxReconnectAttempts: 10,
  reconnectDelay: 3000,
});
```

### ASR Task Updates
```typescript
const { connected, lastStatus } = useWebSocket(taskId);
```

## Connection States

- `connecting`: Initial connection attempt
- `connected`: WebSocket connected and receiving updates
- `disconnected`: Connection lost (will auto-reconnect)
- `error`: Connection error

## Best Practices

1. Always enable auto-reconnect
2. Handle connection state changes in UI
3. Show appropriate status to users
4. Clean up connections on unmount (handled by hook)

## Deprecation Notice

HTTP polling (`/scan/status/{scan_id}`) is deprecated for real-time updates.
Use WebSocket connections instead.
