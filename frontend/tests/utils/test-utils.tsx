// tests/utils/test-utils.tsx
import type { ReactElement } from 'react'
import { render } from '@testing-library/react'

// Temporary wrapper - will be updated after ConfigContext migration
export function renderWithProviders(ui: ReactElement) {
  return render(ui)
}
