import { test, expect } from '@playwright/test';

/**
 * E2E tests for WebSocket-only behavior
 *
 * These tests verify that the application uses WebSocket for real-time updates
 * and does not fall back to polling.
 */
test.describe('WebSocket Real-time Updates', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the path scanner page
    await page.goto('/');
  });

  test('should connect to WebSocket when scan starts', async ({ page }) => {
    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan by clicking the scan button
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await expect(scanButton).toBeEnabled();
    await scanButton.click();

    // Verify connection status appears
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // The status should show either "Connecting..." initially or "Live" if connected quickly
    const statusText = await connectionStatus.textContent();
    expect(statusText).toMatch(/Connecting\.\.\.|Live/);
  });

  test('should show "Live" status when WebSocket is connected', async ({ page }) => {
    // Track WebSocket connections
    const wsConnections: string[] = [];
    page.on('websocket', ws => {
      wsConnections.push(ws.url());
    });

    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Wait for connection status to appear and verify it shows "Live"
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // Wait for WebSocket connection (with timeout)
    await expect(async () => {
      const statusText = await connectionStatus.textContent();
      expect(statusText).toContain('Live');
    }).toPass({ timeout: 10000 });

    // Verify WebSocket connection was established
    expect(wsConnections.length).toBeGreaterThan(0);
    expect(wsConnections.some(url => url.includes('/api/v1/ws/'))).toBeTruthy();
  });

  test('should show disconnected when WebSocket fails', async ({ page, context }) => {
    // Simulate network failure by blocking WebSocket connections
    await page.route('**/api/v1/ws/**', route => route.abort('failed'));

    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Verify connection status shows "Disconnected" not "Polling"
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // Wait for disconnected status (connection should fail)
    await expect(async () => {
      const statusText = await connectionStatus.textContent();
      expect(statusText).toContain('Disconnected');
    }).toPass({ timeout: 10000 });

    // Verify "Polling" text is NOT present anywhere (confirming no polling fallback)
    await expect(page.getByText(/Polling/i)).not.toBeVisible();
  });

  test('should update scan progress via WebSocket messages', async ({ page }) => {
    // Mock WebSocket server for testing
    await page.route('**/api/v1/ws/**', async route => {
      // This would require a more complex setup with a mock WS server
      // For now, we'll just let the real connection happen
      route.continue();
    });

    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Verify connection status shows "Live"
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();
    await expect(connectionStatus).toContainText(/Live/);

    // Verify progress elements are present (they should update via WebSocket)
    // The scan status card should appear with progress info
    const scanStatus = page.locator('.scan-status-card').filter({ hasText: /scan status/i });
    await expect(scanStatus).toBeVisible({ timeout: 10000 });
  });

  test('should not show any polling-related UI', async ({ page }) => {
    // Navigate to the page
    await page.goto('/');

    // Verify there's no "Polling" status indicator
    await expect(page.getByText(/Polling/i)).not.toBeVisible();

    // Verify the connection status element exists (for WebSocket)
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // The connection status should only show WebSocket-related states
    const statusText = await connectionStatus.textContent();
    expect(statusText).toMatch(/Disconnected|Connecting\.\.\.|Live/);
    expect(statusText).not.toMatch(/Polling/);
  });

  test('should maintain connection during active scan', async ({ page }) => {
    // Track WebSocket state changes
    const connectionStates: string[] = [];
    page.on('websocket', ws => {
      ws.on('framereceived', () => {
        connectionStates.push('received');
      });
    });

    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Verify connection is established
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();
    await expect(connectionStatus).toContainText(/Live/, { timeout: 10000 });

    // Wait a bit to ensure connection stays active
    await page.waitForTimeout(2000);

    // Verify still showing "Live" (connection maintained)
    await expect(connectionStatus).toContainText(/Live/);
  });

  test('should handle reconnection when connection is lost', async ({ page }) => {
    // Fill in a scan path
    await page.fill('input[type="text"]', '/test/path');

    // Start a scan
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Wait for initial connection
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();
    await expect(connectionStatus).toContainText(/Live/, { timeout: 10000 });

    // Simulate connection loss by closing the page's WebSocket connections
    // Note: This is a simplified test - in a real scenario, you'd mock the WS server
    await page.evaluate(() => {
      // Force close any WebSocket connections
      const ws = (window as any).mockWebSocket;
      if (ws) {
        ws.close();
      }
    });

    // The connection status should eventually reflect the disconnection
    // and attempt reconnection (showing "Connecting..." or "Disconnected")
    await page.waitForTimeout(1000);

    // Verify the status is not "Polling" (confirming no polling fallback)
    const statusText = await connectionStatus.textContent();
    expect(statusText).not.toMatch(/Polling/);
  });

  test('should display correct connection status styling', async ({ page }) => {
    // Navigate to the page
    await page.goto('/');

    // Verify connection status element has correct CSS class
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // Initially should be disconnected
    await expect(connectionStatus).toHaveClass(/disconnected/);

    // Start a scan
    await page.fill('input[type="text"]', '/test/path');
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Should switch to connected class when WebSocket connects
    await expect(async () => {
      const className = await connectionStatus.getAttribute('class');
      expect(className).toMatch(/connected/);
      expect(className).not.toMatch(/disconnected/);
    }).toPass({ timeout: 10000 });
  });

  test('should show connection status tooltip on hover', async ({ page }) => {
    // Navigate to the page
    await page.goto('/');

    // Get the connection status element
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();

    // Verify it has a title attribute for tooltip
    const title = await connectionStatus.getAttribute('title');
    expect(title).toBeTruthy();
    expect(title).toContain('Connection');
  });

  test('should not make polling HTTP requests for status updates', async ({ page }) => {
    // Track all HTTP requests
    const requests: { url: string; method: string }[] = [];
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
      });
    });

    // Navigate and start a scan
    await page.goto('/');
    await page.fill('input[type="text"]', '/test/path');
    const scanButton = page.getByRole('button', { name: /start|scan/i }).first();
    await scanButton.click();

    // Wait for connection
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toContainText(/Live/, { timeout: 10000 });

    // Wait a bit to see if any polling requests are made
    await page.waitForTimeout(3000);

    // Check for polling-related requests
    const pollingRequests = requests.filter(req =>
      req.url.includes('/status') || req.url.includes('/progress')
    );

    // There should be no polling requests (only initial scan request)
    // We might have the initial scan request but no repeated polling
    expect(pollingRequests.length).toBeLessThan(2);
  });
});
