# Remove Polling, Use WebSocket Only Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove all polling mechanisms from the frontend and use WebSocket as the exclusive real-time communication method.

**Architecture:**
- The current codebase has a comprehensive WebSocket implementation (`useWebSocket.ts`)
- `PathScanner.tsx` contains a polling fallback mechanism (2-second interval) when WebSocket is not connected
- The polling serves as a fallback when WebSocket fails or is disabled
- We will remove the polling logic and improve WebSocket reconnection handling instead

**Tech Stack:**
- Frontend: React + TypeScript
- WebSocket: Native WebSocket API with custom hook (`useWebSocket.ts`)
- Backend: FastAPI WebSocket endpoints at `/api/v1/ws/scan/{scan_id}`

---

## Context

**Current State:**
- **PathScanner.tsx** (lines 84-101): Has a `setInterval` that polls `/asr/scan/status/{scanId}` every 2 seconds when `!useWebsocket || !wsConnected`
- **useWebSocket.ts**: Already has auto-reconnect with exponential backoff (up to 5 attempts, starting at 3 seconds)
- **useASRProcessing.ts**: Already uses WebSocket only, no polling

**Files to Modify:**
- `frontend/src/components/PathScanner.tsx` - Remove polling logic
- `frontend/src/hooks/useWebSocket.ts` - Enhance reconnection logic (optional improvements)
- `frontend/src/hooks/useASRProcessing.ts` - Verify no polling exists (already clean)

**Files to Review:**
- `frontend/src/components/MonitorManager.tsx` - Verify no polling
- `frontend/src/services/api.ts` - Review for any polling-related functions

---

## Task 1: Remove Polling State and Logic from PathScanner

**Files:**
- Modify: `frontend/src/components/PathScanner.tsx:40` (remove `useWebsocket` state)
- Modify: `frontend/src/components/PathScanner.tsx:84-101` (remove polling useEffect)

**Step 1: Write the failing test**

Create test file: `frontend/src/components/PathScanner.test.update.tsx`

```tsx
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../hooks/useWebSocket';

// Verify that WebSocket hook handles disconnection properly
describe('PathScanner - WebSocket Only Mode', () => {
  it('should not have useWebsocket state toggle', () => {
    // This test verifies that the component always uses WebSocket
    // After implementation, there should be no way to disable WebSocket
    const { useWebsocket } = require('../components/PathScanner');
    // The component should not have a useWebsocket state
    expect(useWebsocket).toBeUndefined();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- PathScanner.test.update.tsx`
Expected: FAIL or shows that `useWebsocket` state exists

**Step 3: Remove the useWebsocket state**

In `frontend/src/components/PathScanner.tsx`:

Remove line 40:
```typescript
const [useWebsocket, setUseWebSocket] = useState(true);
```

**Step 4: Remove the polling useEffect**

In `frontend/src/components/PathScanner.tsx`, remove lines 84-101:

```typescript
// DELETE THIS ENTIRE useEffect BLOCK:
// Poll scan status if there's an active scan and WebSocket is not connected
useEffect(() => {
  let intervalId: ReturnType<typeof setInterval> | null = null;

  // Only use polling if WebSocket is not connected or not enabled
  const shouldUsePolling = activeScanId && isScanning && (!useWebsocket || !wsConnected);

  if (shouldUsePolling) {
    intervalId = setInterval(() => {
      fetchScanStatus(activeScanId);
    }, 2000); // Poll every 2 seconds
  }

  return () => {
    if (intervalId) {
      clearInterval(intervalId);
    }
  };
}, [activeScanId, isScanning, wsConnected, useWebsocket]);
```

**Step 5: Update connection status display**

In `frontend/src/components/PathScanner.tsx`, update lines 237-242:

Change from:
```tsx
<span className="status-text">
  {wsConnected ? 'Live' : wsStatus === 'connecting' ? 'Connecting...' : 'Polling'}
</span>
```

To:
```tsx
<span className="status-text">
  {wsConnected ? 'Live' : wsStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
</span>
```

**Step 6: Update the connection status title**

In `frontend/src/components/PathScanner.tsx`, update line 236:

Change from:
```tsx
title={`WebSocket: ${wsStatus}${wsError ? ` - ${wsError}` : ''}`}
```

To:
```tsx
title={`Connection: ${wsStatus}${wsError ? ` - ${wsError}` : ''}`}
```

**Step 7: Remove unused imports if any**

Check if `setUseWebSocket` was exported or used elsewhere. Remove if unused.

**Step 8: Run tests to verify changes**

Run: `cd frontend && npm test -- PathScanner.test.tsx`
Expected: PASS

**Step 9: Commit**

```bash
git add frontend/src/components/PathScanner.tsx frontend/src/components/PathScanner.test.update.tsx
git commit -m "refactor: remove polling fallback, use WebSocket only in PathScanner

- Remove useWebsocket state toggle
- Remove polling useEffect that called fetchScanStatus every 2 seconds
- Update connection status display to show 'Disconnected' instead of 'Polling'
- WebSocket is now the exclusive real-time communication method"
```

---

## Task 2: Enhance WebSocket Reconnection Logic (Optional but Recommended)

**Files:**
- Modify: `frontend/src/hooks/useWebSocket.ts`

**Purpose:** Since we removed polling fallback, ensure WebSocket reconnection is robust.

**Step 1: Review current reconnection settings**

Current settings in `useWebSocket.ts`:
- `maxReconnectAttempts: 5`
- `reconnectDelay: 3000` (3 seconds)
- Exponential backoff: `delay * reconnectAttemptsRef.current`

**Step 2: Consider increasing max reconnection attempts**

In `frontend/src/hooks/useWebSocket.ts`, update the default `maxReconnectAttempts`:

Change from:
```typescript
maxReconnectAttempts = 5,
```

To:
```typescript
maxReconnectAttempts = 10,  // Increased for better reliability
```

**Step 3: Add infinite reconnection option (optional enhancement)**

Add a new option to `UseWebSocketOptions` interface:

```typescript
/** Enable infinite reconnection attempts (default: false) */
infiniteReconnect?: boolean;
```

Update the reconnection logic to support infinite attempts:

In the `ws.addEventListener('close', ...)` handler, update line 182:

Change from:
```typescript
if (autoReconnect && !event.wasClean && reconnectAttemptsRef.current < maxReconnectAttempts) {
```

To:
```typescript
if (autoReconnect && !event.wasClean && (infiniteReconnect || reconnectAttemptsRef.current < maxReconnectAttempts)) {
```

**Step 4: Update type definitions**

In `frontend/src/types/websocket.ts`, add the new option to `WSConnectionOptions`:

```typescript
/** Enable infinite reconnection attempts (default: false) */
infiniteReconnect?: boolean;
```

**Step 5: Run tests**

Run: `cd frontend && npm test -- useWebSocket.test.ts`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/hooks/useWebSocket.ts frontend/src/types/websocket.ts
git commit -m "feat: increase WebSocket max reconnection attempts to 10

- Increased maxReconnectAttempts from 5 to 10 for better reliability
- Added infiniteReconnect option for continuous reconnection attempts
- Ensures better uptime when network is unstable"
```

---

## Task 3: Verify No Other Polling in Codebase

**Files:**
- Review: `frontend/src/components/MonitorManager.tsx`
- Review: `frontend/src/hooks/useASRProcessing.ts`
- Review: `frontend/src/services/api.ts`

**Step 1: Search for setInterval patterns**

Run: `cd frontend && grep -r "setInterval" src/ --include="*.ts" --include="*.tsx"`

Expected output should only show:
- `useWebSocket.ts` - for heartbeat (30 second ping interval, acceptable)
- No other setInterval calls for polling

**Step 2: Search for setTimeout patterns that might be polling**

Run: `cd frontend && grep -r "setTimeout" src/ --include="*.ts" --include="*.tsx" -A 2 -B 2`

Review each setTimeout to ensure none are used for recursive polling.

**Step 3: Verify useASRProcessing uses WebSocket only**

Review `frontend/src/hooks/useASRProcessing.ts`:
- Line 74: Uses `useWebSocket(taskIdRef.current)` for updates
- No polling logic exists (confirmed from earlier review)

**Step 4: Verify MonitorManager has no polling**

Run: `cat frontend/src/components/MonitorManager.tsx | grep -E "(setInterval|setTimeout|poll)"`

Expected: No matches

**Step 5: Document findings**

If no other polling is found, no changes needed. Create a summary:

```bash
cat > frontend/POLLING_AUDIT.md << 'EOF'
# Polling Audit Report

Date: 2026-02-08

## Findings

### Removed Polling
- **PathScanner.tsx**: Removed 2-second polling fallback for scan status

### Existing Intervals (Not Polling)
- **useWebSocket.ts**: 30-second heartbeat/ping interval (keep-alive, not polling)

### Verified Clean
- **useASRProcessing.ts**: Uses WebSocket only, no polling
- **MonitorManager.tsx**: No polling, loads data on user actions only
- **api.ts**: No polling functions, all one-time API calls

## Conclusion
All polling mechanisms have been removed. Real-time updates are exclusively via WebSocket.
EOF
```

**Step 6: Commit audit documentation**

```bash
git add frontend/POLLING_AUDIT.md
git commit -m "docs: add polling audit report

- Documents removal of all polling mechanisms
- Confirms WebSocket is the exclusive real-time communication method
- Lists remaining setInterval uses (WebSocket heartbeat only)"
```

---

## Task 4: Update Tests for WebSocket-Only Behavior

**Files:**
- Modify: `frontend/src/components/PathScanner.test.tsx`
- Modify: `frontend/src/hooks/useWebSocket.test.ts`

**Step 1: Update PathScanner tests**

In `frontend/src/components/PathScanner.test.tsx`, remove any tests related to polling mode.

Find and remove tests that:
- Test `useWebsocket` state toggle
- Test polling behavior when WebSocket is disconnected
- Test fallback to HTTP polling

**Step 2: Add WebSocket connection tests**

Add new test to verify WebSocket is always used:

```typescript
describe('PathScanner - WebSocket Only', () => {
  it('should always use WebSocket for scan updates', () => {
    const { result } = renderHook(() => useWebSocket('test-scan-id'));

    // Verify WebSocket hook is called when scan starts
    expect(result.current.status).toBe('connecting');
  });

  it('should show disconnected status when WebSocket fails', async () => {
    // Mock WebSocket connection failure
    const { getByTestId } = render(<PathScanner />);

    // Start a scan
    // Simulate WebSocket failure
    // Verify status shows "Disconnected" not "Polling"
  });
});
```

**Step 3: Update useWebSocket tests**

Add tests for improved reconnection:

```typescript
describe('useWebSocket - Enhanced Reconnection', () => {
  it('should reconnect up to maxReconnectAttempts', async () => {
    // Test reconnection limit
  });

  it('should use exponential backoff for reconnection', async () => {
    // Test backoff timing
  });

  it('should support infinite reconnection when enabled', async () => {
    // Test infinite reconnection option
  });
});
```

**Step 4: Run all tests**

Run: `cd frontend && npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add frontend/src/components/PathScanner.test.tsx frontend/src/hooks/useWebSocket.test.ts
git commit -m "test: update tests for WebSocket-only behavior

- Remove polling-related tests
- Add WebSocket-only behavior tests
- Add enhanced reconnection tests
- Verify 'Disconnected' status is shown instead of 'Polling'"
```

---

## Task 5: Update Documentation

**Files:**
- Modify: `backend/docs/WEBSOCKET_API.md`
- Create: `frontend/docs/WEBSOCKET_USAGE.md` (if docs directory exists)

**Step 1: Update backend WebSocket documentation**

In `backend/docs/WEBSOCKET_API.md`, add a note about WebSocket being the only real-time method:

Add after line 9:
```markdown
## Important

WebSocket is the exclusive real-time communication method for this application.
All clients must use WebSocket for receiving scan status updates and ASR processing progress.
HTTP polling endpoints (`/scan/status/{scan_id}`) are deprecated and should not be used for real-time updates.
```

**Step 2: Create frontend WebSocket usage guide**

Create `frontend/docs/WEBSOCKET_USAGE.md`:

```markdown
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
```

**Step 3: Update README if needed**

Check if `frontend/README.md` or root `README.md` mentions WebSocket or polling.
Update any references to polling.

**Step 4: Commit**

```bash
git add backend/docs/WEBSOCKET_API.md frontend/docs/WEBSOCKET_USAGE.md
git commit -m "docs: update WebSocket documentation

- Add deprecation notice for HTTP polling
- Create frontend WebSocket usage guide
- Document WebSocket as exclusive real-time method"
```

---

## Task 6: Backend - Deprecate Polling Endpoints (Optional)

**Files:**
- Modify: `backend/app/api/endpoints/asr.py`
- Modify: `backend/app/api/endpoints/websocket.py`

**Purpose:** Add deprecation warnings to HTTP polling endpoints.

**Step 1: Add deprecation header to scan status endpoint**

In `backend/app/api/endpoints/asr.py`, update the `get_scan_status` function (line 414):

Add deprecation header:
```python
from fastapi import Response

@router.get("/scan/status/{scan_id}", response_model=ScanStatus)
async def get_scan_status(scan_id: str, response: Response):
    """
    Get the status of a scan operation

    ⚠️ DEPRECATED: This endpoint is deprecated for real-time updates.
    Use WebSocket connection at /api/v1/ws/scan/{scan_id} instead.

    Args:
        scan_id: Scan ID to check status for
    """
    response.headers["X-Deprecation"] = "Use WebSocket endpoint /api/v1/ws/scan/{scan_id} for real-time updates"
    response.headers["Sunset"] = "2026-06-01"  # Deprecation date

    scan_status = scan_service.get_scan_status(scan_id)
    if not scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_status
```

**Step 2: Add similar deprecation to any other polling endpoints**

Check for other endpoints that might be used for polling:
- `/scan/result/{scan_id}` - This is fine (one-time fetch)
- `/scan/all` - This is fine (one-time fetch)

Only `/scan/status/{scan_id}` needs deprecation warning.

**Step 3: Run backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/api/endpoints/asr.py
git commit -m "feat: add deprecation warning to HTTP polling endpoint

- Add X-Deprecation header to /scan/status/{scan_id}
- Document WebSocket alternative in docstring
- Set Sunset date for future removal"
```

---

## Task 7: E2E Testing

**Files:**
- Create: `frontend/e2e/websocket-only.spec.ts` (if using Playwright/Cypress)

**Step 1: Create E2E test for WebSocket behavior**

```typescript
import { test, expect } from '@playwright/test';

test.describe('WebSocket Real-time Updates', () => {
  test('should connect to WebSocket when scan starts', async ({ page }) => {
    await page.goto('/');

    // Start a scan
    await page.fill('[data-testid="scan-path-input"]', '/test/path');
    await page.click('[data-testid="start-scan-button"]');

    // Verify connection status changes to "Live"
    await expect(page.locator('[data-testid="connection-status"]')).toHaveText(/Live/);
  });

  test('should show disconnected when WebSocket fails', async ({ page, context }) => {
    // Simulate network failure
    await context.setOffline(true);

    await page.goto('/');
    // Start a scan...
    // Verify status shows "Disconnected" not "Polling"
    await expect(page.locator('[data-testid="connection-status"]')).toHaveText(/Disconnected/);
  });
});
```

**Step 2: Run E2E tests**

Run: `cd frontend && npm run test:e2e`
Expected: PASS

**Step 3: Commit**

```bash
git add frontend/e2e/websocket-only.spec.ts
git commit -m "test: add E2E tests for WebSocket-only behavior

- Test WebSocket connection on scan start
- Test disconnected status display
- Verify no polling fallback occurs"
```

---

## Summary

After completing all tasks:

1. ✅ **Polling removed from PathScanner.tsx** - No more `setInterval` for scan status
2. ✅ **WebSocket reconnection enhanced** - Increased attempts and optional infinite reconnect
3. ✅ **Codebase audited** - Verified no other polling exists
4. ✅ **Tests updated** - WebSocket-only behavior tested
5. ✅ **Documentation updated** - WebSocket as exclusive method documented
6. ✅ **Backend endpoints deprecated** - HTTP polling endpoints marked as deprecated
7. ✅ **E2E tests added** - Real-world WebSocket behavior verified

## Verification Checklist

- [ ] No `setInterval` calls for polling exist in frontend code
- [ ] Connection status shows "Disconnected" instead of "Polling"
- [ ] WebSocket reconnects automatically when connection drops
- [ ] All tests pass (unit, integration, E2E)
- [ ] Documentation reflects WebSocket-only approach
- [ ] Backend endpoints have deprecation warnings
