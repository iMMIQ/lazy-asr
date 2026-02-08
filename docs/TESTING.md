# Testing Guide

This document describes the testing architecture and how to run tests in the lazy-asr project.

## Test Architecture Overview

The project follows a test pyramid approach:

```
          E2E Tests (Playwright)
         /                    \
    Integration Tests          Unit Tests
    (API + DB)              (Fast, Isolated)
```

### Test Types

| Type | Framework | Purpose | Location |
|------|-----------|---------|----------|
| Unit | pytest / Vitest | Test isolated functions and components | `backend/tests/unit/`, `frontend/tests/unit/` |
| Integration | pytest | Test API endpoints with database | `backend/tests/integration/` |
| Component | Vitest | Test React components | `frontend/tests/components/` |
| E2E | Playwright | Test complete user workflows | `e2e/tests/` |

## Running Tests

### Run All Tests

```bash
./scripts/test.sh
```

### Backend Tests

```bash
# Run all backend tests
cd backend
pytest

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run with coverage
pytest --cov=app --cov-report=html

# Using the script
./backend/scripts/test.sh unit
./backend/scripts/test.sh integration
./backend/scripts/test.sh coverage
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in UI mode
npm run test:ui

# Run tests once
npm run test:run

# Run with coverage
npm run test:coverage
```

### E2E Tests

```bash
cd frontend

# Install Playwright browsers (first time only)
npm run test:e2e:install

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# Debug E2E tests
npm run test:e2e:debug
```

## Test Structure

### Backend Structure

```
backend/tests/
├── conftest.py              # Pytest fixtures and configuration
├── factories.py             # Test data factories
├── unit/                    # Unit tests
│   ├── test_core/
│   ├── test_db/
│   ├── test_services/
│   └── test_utils/
└── integration/             # Integration tests
    └── test_api_endpoints.py
```

### Frontend Structure

```
frontend/tests/
├── setup.ts                 # Vitest setup
├── mocks/                   # MSW API mocks
│   ├── setup.ts
│   └── handlers.ts
├── utils/                   # Test utilities
│   └── test-utils.tsx
├── unit/                    # Unit tests
│   ├── utils/
│   └── services/
└── components/              # Component tests
    └── *.test.tsx
```

### E2E Structure

```
e2e/
├── playwright.config.ts     # Playwright configuration
├── tests/                   # E2E test files
│   └── scan-workflow.spec.ts
└── fixtures/                # Test data and helpers
    ├── test-data.json
    └── test-helpers.ts
```

## Writing Tests

### Backend Unit Tests

```python
import pytest
from tests.factories import TaskFactory

@pytest.mark.unit
def test_task_creation():
    task = TaskFactory.create(status="pending")
    assert task["status"] == "pending"
```

### Backend Integration Tests

```python
import pytest

@pytest.mark.integration
async def test_create_task(client):
    response = await client.post("/api/tasks", json={"filename": "test.wav"})
    assert response.status_code == 201
```

### Frontend Unit Tests

```typescript
import { describe, it, expect } from 'vitest'
import { formatDuration } from './formatters'

describe('formatDuration', () => {
  it('formats seconds to MM:SS', () => {
    expect(formatDuration(125)).toBe('02:05')
  })
})
```

### Frontend Component Tests

```typescript
import { render, screen } from '@testing-library/react'
import { renderWithProviders } from '../tests/utils/test-utils'

describe('TaskList', () => {
  it('renders empty state', () => {
    renderWithProviders(<TaskList tasks={[]} />)
    expect(screen.getByText(/no tasks/i)).toBeInTheDocument()
  })
})
```

### E2E Tests

```typescript
import { test, expect } from '@playwright/test'

test('complete scan workflow', async ({ page }) => {
  await page.goto('/')
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles('test.wav')
  await page.click('button:has-text("Start")')
  await expect(page.getByText(/completed/i)).toBeVisible()
})
```

## Coverage Goals

| Layer | Target Coverage |
|-------|----------------|
| Backend (statements) | 70% |
| Frontend (statements) | 70% |
| Critical paths | 90%+ |

## CI/CD

Tests run automatically on:
- Every push to `master`, `main`, or `develop`
- Every pull request

The CI pipeline:
1. Runs unit tests for both backend and frontend
2. Runs integration tests
3. Runs type checking (mypy, tsc)
4. Runs E2E tests (only after other tests pass)
5. Uploads coverage reports to Codecov

## Troubleshooting

### Backend tests failing with database errors
- Ensure tests use the `test_db` fixture for database isolation
- Check that async tests use `async def` and `await`

### Frontend tests failing with import errors
- Ensure `vitest.config.ts` has correct aliases configured
- Check that `tsconfig.json` paths match the alias configuration

### E2E tests failing with timeout
- Increase timeout in `playwright.config.ts`
- Ensure the dev server is running on the expected port
- Check that backend API is accessible

### MSW handlers not matching requests
- Verify the URL path matches exactly (including leading `/`)
- Check that the HTTP method (GET, POST, etc.) matches
- Ensure `tests/mocks/setup.ts` is imported in vitest setup
