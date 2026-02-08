/**
 * Test utility functions for React Testing Library
 *
 * These helpers provide common wrappers and configurations
 * for rendering components in tests.
 */
import type { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Custom render function that wraps with necessary providers
type CustomRenderOptions = Omit<RenderOptions, 'wrapper'> & {
  wrapper?: React.ComponentType<{ children: React.ReactNode }>
}

/**
 * Render with custom providers. Extend this as you add more context providers.
 *
 * @example
 * ```tsx
 * renderWithProviders(<MyComponent />, {
 *   wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>
 * })
 * ```
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: CustomRenderOptions
) {
  return render(ui, options)
}

/**
 * Create a mock function with TypeScript types
 */
export function createMockFn<T extends (...args: any[]) => any>(
  implementation?: T
): ReturnType<typeof vi.fn> {
  const mock = implementation || vi.fn()
  return mock as any
}

/**
 * Wait for async operations to complete
 */
export async function flushPromises(): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, 0))
}

/**
 * Create a mock file object for file upload testing
 */
export function createMockFile(
  name: string,
  content: string | Blob,
  mimeType: string
): File {
  const file = new File([content], name, { type: mimeType })
  Object.defineProperty(file, 'size', { value: content instanceof Blob ? content.size : content.length })
  return file
}

/**
 * Mock window.matchMedia for responsive component testing
 */
export function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}
