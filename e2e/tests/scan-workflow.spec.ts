import { test, expect } from '@playwright/test'

test.describe('Scan Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display the main page', async ({ page }) => {
    await expect(page).toHaveTitle(/Lazy ASR/)
  })

  test('should show upload area', async ({ page }) => {
    const uploadArea = page.getByText(/upload/i).or(page.locator('[data-testid="upload-area"]'))
    await expect(uploadArea).toBeVisible()
  })

  test('should handle file selection', async ({ page }) => {
    // Find file input (usually hidden)
    const fileInput = page.locator('input[type="file"]')

    // Create a mock file
    const file = await page.evaluate(() => ({
      name: 'test-audio.wav',
      mimeType: 'audio/wav',
      buffer: Buffer.from('mock audio data').toString('base64'),
    }))

    // Upload the file
    await fileInput.setInputFiles({
      name: 'test-audio.wav',
      mimeType: 'audio/wav',
      buffer: Buffer.from('mock audio data'),
    })

    // Verify file was selected
    await expect(page.getByText(/test-audio\.wav/)).toBeVisible()
  })

  test('should start scan when button clicked', async ({ page }) => {
    // Upload file first
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.wav',
      mimeType: 'audio/wav',
      buffer: Buffer.from('mock data'),
    })

    // Click scan button
    const scanButton = page.getByRole('button', { name: /start|scan/i }).or(page.locator('[data-testid="start-scan"]'))
    await scanButton.click()

    // Verify scan started (look for progress indicator)
    await expect(page.getByText(/progress|scanning/i)).toBeVisible({ timeout: 5000 })
  })

  test('should display scan results', async ({ page }) => {
    // This test assumes backend returns mock data or we use API mocking
    await page.goto('/')

    // Upload file
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.wav',
      mimeType: 'audio/wav',
      buffer: Buffer.from('mock data'),
    })

    // Start scan
    const scanButton = page.getByRole('button', { name: /start|scan/i })
    await scanButton.click()

    // Wait for completion (may need to increase timeout for real tests)
    await expect(page.getByText(/completed|done|result/i)).toBeVisible({ timeout: 30000 })
  })
})

test.describe('Task Management', () => {
  test('should display task list', async ({ page }) => {
    await page.goto('/tasks')

    // Should show task list container
    await expect(page.locator('[data-testid="task-list"]').or(page.getByText(/tasks/i))).toBeVisible()
  })

  test('should allow task cancellation', async ({ page }) => {
    await page.goto('/tasks')

    // Find cancel button on a pending task
    const cancelButton = page.getByRole('button', { name: /cancel/i }).first()

    if (await cancelButton.isVisible()) {
      await cancelButton.click()
      await expect(page.getByText(/cancelled/i)).toBeVisible()
    }
  })

  test('should allow task deletion', async ({ page }) => {
    await page.goto('/tasks')

    // Find delete button
    const deleteButton = page.getByRole('button', { name: /delete|remove/i }).first()

    if (await deleteButton.isVisible()) {
      // Handle confirmation dialog if present
      page.on('dialog', dialog => dialog.accept())

      await deleteButton.click()
      await expect(page.getByText(/deleted|removed/i)).toBeVisible()
    }
  })
})

test.describe('Navigation', () => {
  test('should navigate between pages', async ({ page }) => {
    await page.goto('/')

    // Navigate to tasks page
    await page.click('a[href="/tasks"]')
    await expect(page).toHaveURL(/\/tasks/)

    // Navigate back to home
    await page.click('a[href="/"]')
    await expect(page).toHaveURL('/')
  })
})

test.describe('Error Handling', () => {
  test('should show error for invalid file type', async ({ page }) => {
    await page.goto('/')

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('not an audio file'),
    })

    await expect(page.getByText(/invalid|not supported|audio/i)).toBeVisible({ timeout: 5000 })
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/scan', route => route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    }))

    await page.goto('/')

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.wav',
      mimeType: 'audio/wav',
      buffer: Buffer.from('mock data'),
    })

    const scanButton = page.getByRole('button', { name: /start|scan/i })
    await scanButton.click()

    await expect(page.getByText(/error|failed/i)).toBeVisible({ timeout: 5000 })
  })
})
