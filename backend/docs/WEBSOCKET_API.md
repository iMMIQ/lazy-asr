# WebSocket API Documentation

## Overview

This document describes the WebSocket API for real-time updates in the Lazy ASR service. The WebSocket API enables clients to receive live progress updates for ASR (Automatic Speech Recognition) processing and path scanning operations.

## Base URL

```
ws://localhost:8000/api/v1/ws
```

For production with HTTPS:
```
wss://your-domain.com/api/v1/ws
```

## Connection Endpoints

### Scan Updates Endpoint

Subscribe to updates for a specific scan operation by scan ID.

**URL Pattern:** `/api/v1/ws/scan/{scan_id}`

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/scan/scan-123');
```

### General WebSocket Endpoint

Alternative endpoint using query parameter for scan ID.

**URL Pattern:** `/api/v1/ws?scan_id={scan_id}`

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws?scan_id=scan-123');
```

### Task Updates Endpoint

Subscribe to updates for a specific ASR processing task by task ID.

**URL Pattern:** `/api/v1/ws/task/{task_id}`

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/task/task-abc-123');
```

## Message Format

All WebSocket messages follow this structure:

```typescript
{
  "type": string,           // Message type: 'status', 'error', 'ping', 'pong'
  "data": object,           // Message-specific data
  "message?: string,        // Optional human-readable message
  "timestamp?: string       // ISO 8601 timestamp
}
```

## Message Types

### Status Message

Sent when there's a status update for a scan or task.

```json
{
  "type": "status",
  "data": {
    "scan_id": "scan-123",
    "status": "scanning",
    "progress": 45,
    "total_files": 100,
    "processed_files": 45,
    "current_file": "/path/to/current/audio.wav",
    "error": null
  }
}
```

### ASR Progress Message

Sent during ASR processing to report progress.

```json
{
  "type": "status",
  "data": {
    "task_id": "task-abc-123",
    "stage": "transcription",
    "progress": 65,
    "message": "Processing segment 13/20",
    "media_path": "audio.wav",
    "current_segment": 13,
    "total_segments": 20,
    "stats": {
      "total_segments": 20,
      "successful_transcriptions": 12,
      "failed_segments": 0,
      "empty_segments": 1,
      "total_subtitles": 145,
      "output_formats": ["srt", "vtt"]
    }
  }
}
```

### Error Message

Sent when an error occurs during processing.

```json
{
  "type": "error",
  "data": {
    "task_id": "task-abc-123",
    "error": "Processing failed: Unsupported audio format",
    "error_type": "ValidationError"
  },
  "message": "An error occurred during processing"
}
```

### Ping/Pong Messages

Used for heartbeat/connection keep-alive.

**Client sends:**
```json
{
  "type": "ping",
  "data": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Server responds:**
```json
{
  "type": "pong",
  "data": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Processing Stages

ASR processing reports the following stages:

| Stage | Description | Progress Range |
|-------|-------------|----------------|
| `idle` | Initial state | 0% |
| `preparing` | Media file preparation | 5% |
| `vad_segmentation` | Voice activity detection | 10-20% |
| `loading_plugin` | ASR plugin loading | 30% |
| `exporting_segments` | Speech segment export | 20% |
| `transcription` | Speech transcription | 40-80% |
| `generating_subtitles` | Subtitle file generation | 85-95% |
| `completed` | Processing complete | 100% |
| `error` | Processing failed | N/A |

## Connection Lifecycle

### 1. Establish Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/scan/scan-123');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('WebSocket disconnected:', event.code, event.reason);
};
```

### 2. Receive Messages

```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'status':
      handleStatusUpdate(message.data);
      break;
    case 'error':
      handleError(message.data);
      break;
    case 'pong':
      handlePong();
      break;
  }
};
```

### 3. Send Messages

```javascript
// Send ping for heartbeat
ws.send(JSON.stringify({
  type: 'ping',
  data: { timestamp: new Date().toISOString() }
}));
```

### 4. Close Connection

```javascript
ws.close(1000, 'Client closing connection');
```

## Error Handling

### Connection Errors

- **1000**: Normal closure
- **1001**: Endpoint going away
- **1002**: Protocol error
- **1003**: Unsupported data
- **1006**: Abnormal closure
- **1008**: Policy violation
- **1009**: Message too big
- **1010**: Missing extension
- **1011**: Internal error
- **1015**: TLS handshake failure

### Message Validation

The server validates scan_id and task_id parameters:
- Minimum length: 1 character
- Maximum length: 100 characters
- Invalid characters: newline, carriage return, null, `<`, `>`, `&`

Invalid IDs will result in an error message and immediate connection closure.

## Client Implementation Examples

### React Hook Example

```typescript
import { useEffect, useState, useCallback, useRef } from 'react';

export function useWebSocket(taskId: string | null) {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!taskId) return;

    setStatus('connecting');
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/task/${taskId}`);
    wsRef.current = ws;

    ws.onopen = () => setStatus('connected');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLastMessage(message);
    };
    ws.onerror = () => setStatus('error');
    ws.onclose = () => setStatus('disconnected');
  }, [taskId]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setStatus('disconnected');
  }, []);

  useEffect(() => {
    if (taskId) {
      connect();
      return () => disconnect();
    }
  }, [taskId, connect, disconnect]);

  return { status, lastMessage, disconnect, reconnect: connect };
}
```

### Vanilla JavaScript Example

```javascript
class ASRWebSocketClient {
  constructor(taskId) {
    this.taskId = taskId;
    this.ws = null;
    this.listeners = new Map();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/api/v1/ws/task/${this.taskId}`);

    this.ws.onopen = () => {
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.emit('message', message);
      this.emit(message.type, message.data);
    };

    this.ws.onerror = (error) => {
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      this.emit('disconnected');
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  send(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }
}

// Usage
const client = new ASRWebSocketClient('task-123');
client.connect();
client.on('status', (data) => {
  console.log('Progress:', data.progress, '%');
  console.log('Stage:', data.stage);
});
client.on('error', (data) => {
  console.error('Error:', data.error);
});
```

## Rate Limiting and Best Practices

1. **Reconnection**: Implement exponential backoff for reconnection attempts
2. **Heartbeat**: Send ping messages every 30 seconds to keep connection alive
3. **Message Throttling**: Handle high-frequency messages appropriately in UI
4. **Error Recovery**: Gracefully handle connection drops and retry
5. **Resource Cleanup**: Always close connections when component unmounts

## Security Considerations

1. **Authentication**: WebSocket connections inherit authentication from the HTTP session
2. **Authorization**: Verify user has permission to access the requested scan/task
3. **Input Validation**: All scan_id and task_id parameters are validated
4. **Message Size**: Large messages may be rejected or truncated

## Testing

### WebSocket Testing Tools

- **wscat**: Command-line WebSocket client
  ```bash
  wscat -c "ws://localhost:8000/api/v1/ws/scan/scan-123"
  ```

- **Postman**: Supports WebSocket connections
- **Browser DevTools**: Network tab shows WebSocket frames

### Example Test Sequence

```bash
# Connect to scan updates
wscat -c "ws://localhost:8000/api/v1/ws/scan/scan-123"

# Expected messages:
# < {"type":"status","data":{"scan_id":"scan-123","status":"scanning","progress":0}}
# < {"type":"status","data":{"scan_id":"scan-123","status":"scanning","progress":50}}
# < {"type":"status","data":{"scan_id":"scan-123","status":"completed","progress":100}}

# Send ping
> {"type":"ping"}

# Expected response:
# < {"type":"pong"}
```

## API Versioning

The current API version is `v1`. Future versions will be:
- `/api/v2/ws/...` for version 2
- Backward compatibility will be maintained where possible

## Support and Feedback

For issues or questions regarding the WebSocket API:
1. Check this documentation first
2. Review the error messages received
3. Check server logs for additional context
4. Report bugs with connection details and message logs
