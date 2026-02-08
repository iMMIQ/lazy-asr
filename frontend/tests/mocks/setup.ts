/**
 * MSW (Mock Service Worker) setup for Vitest
 *
 * This file sets up the mock server for API interception in tests.
 */
import { afterAll, afterEach, beforeAll } from 'vitest'
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

// Create MSW server with handlers
export const server = setupServer(...handlers)

// Setup and teardown for MSW
beforeAll(() => {
  server.listen({
    onUnhandledRequest: 'warn',  // Use 'warn' instead of 'error' to avoid failures
  })
})

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => {
  server.close()
})
