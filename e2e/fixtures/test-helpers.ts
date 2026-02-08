/**
 * E2E test helper functions
 *
 * These utilities provide common actions and assertions for E2E tests.
 */
import { Page, Locator } from '@playwright/test'

/**
 * Navigate to a page and wait for it to be ready
 */
export async function navigateTo(page: Page, path: string) {
  await page.goto(path)
  await page.waitForLoadState('networkidle')
}

/**
 * Upload a file through the file input
 */
export async function uploadFile(
  page: Page,
  fileName: string,
  mimeType: string = 'audio/wav'
) {
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles({
    name: fileName,
    mimeType,
    buffer: Buffer.from('mock audio data for testing')
  })
}

/**
 * Wait for a task to complete (with timeout)
 */
export async function waitForTaskCompletion(
  page: Page,
  taskId: string,
  timeout: number = 30000
) {
  await page.waitForSelector(
    `[data-testid="task-${taskId}"][data-status="completed"]`,
    { timeout }
  )
}

/**
 * Get toast/notification message
 */
export async function getToastMessage(page: Page): Promise<string> {
  const toast = page.locator('[data-testid="toast"], .toast, [role="alert"]').first()
  await toast.waitFor({ state: 'visible' })
  return await toast.textContent() || ''
}

/**
 * Create a mock audio file blob
 */
export function createMockAudioFile(
  fileName: string = 'test.wav',
  duration: number = 1000
): Buffer {
  // Create a minimal WAV file header + silence
  const sampleRate = 16000
  const numSamples = (sampleRate * duration) / 1000
  const byteRate = sampleRate * 2

  const buffer = Buffer.alloc(44 + numSamples * 2)

  // WAV header
  buffer.write('RIFF', 0)
  buffer.writeUInt32LE(36 + numSamples * 2, 4)
  buffer.write('WAVE', 8)
  buffer.write('fmt ', 12)
  buffer.writeUInt32LE(16, 16)
  buffer.writeUInt16LE(1, 20) // PCM
  buffer.writeUInt16LE(1, 22) // Mono
  buffer.writeUInt32LE(sampleRate, 24)
  buffer.writeUInt32LE(byteRate, 28)
  buffer.writeUInt16LE(2, 32) // Block align
  buffer.writeUInt16LE(16, 34) // Bits per sample
  buffer.write('data', 36)
  buffer.writeUInt32LE(numSamples * 2, 40)

  return buffer
}

/**
 * Login helper (if auth is added)
 */
export async function login(page: Page, username: string, password: string) {
  await page.goto('/login')
  await page.fill('input[name="username"]', username)
  await page.fill('input[name="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL('/')
}

/**
 * Mock API response
 */
export async function mockApiResponse(
  page: Page,
  url: string,
  response: any,
  status: number = 200
) {
  await page.route(url, route => route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(response)
  }))
}

/**
 * Wait for loading state to finish
 */
export async function waitForLoading(page: Page) {
  await page.waitForSelector('[data-loading="true"], .loading, [aria-busy="true"]', { state: 'hidden' })
}
