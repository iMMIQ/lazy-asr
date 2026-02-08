# Polling Audit Report

Date: 2026-02-08

## Findings

### Removed Polling
- **PathScanner.tsx**: Removed 2-second polling fallback for scan status

### Existing Intervals (Not Polling)
- **useWebSocket.ts**: 30-second heartbeat/ping interval (keep-alive, not polling)
  - Line 152-156: `setInterval` used for WebSocket heartbeat/ping messages
  - Line 189-191: `setTimeout` used for reconnection attempts with exponential backoff

### Verified Clean
- **useASRProcessing.ts**: Uses WebSocket only, no polling
  - Line 74: Subscribes to `useWebSocket` for real-time task updates
  - Lines 77-95: Handles WebSocket status updates via `useEffect`

- **MonitorManager.tsx**: No polling, loads data on user actions only
  - Loads monitors and service status once on mount (lines 39-42)
  - All subsequent data loads are triggered by user actions (buttons)

- **api.ts**: No polling functions, all one-time API calls
  - All functions are single-request API calls using axios
  - No interval or timeout patterns

## Conclusion
All polling mechanisms have been removed. Real-time updates are exclusively via WebSocket.
