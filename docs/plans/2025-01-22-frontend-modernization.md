# Frontend Modernization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate frontend from Create React App + JavaScript to Vite + TypeScript with comprehensive test coverage and CSS modules.

**Architecture:** Gradual migration in place - upgrade build tooling first, establish test infrastructure, then migrate modules from bottom-up (utils → services → context → hooks → components).

**Tech Stack:** Vite 5, TypeScript 5, Vitest, React Testing Library, MSW, CSS Modules

**Current State:**
- React 19.2.0 + Create React App
- All files are `.js` (TypeScript installed but unused)
- Single `App.css` with 2500+ lines
- No tests

**Target State:**
- Vite dev server with hot reload
- Full TypeScript strict mode
- Vitest unit + integration tests
- CSS modules for components
- Preserved glassmorphism design

---

## Phase 0: Pre-work & Backup

### Task 0.1: Create baseline backup

**Files:**
- None (git operation)

**Step 1: Create git tag for current state**

```bash
git tag -a pre-refactor -m "Baseline before frontend modernization"
git push origin pre-refactor
```

**Step 2: Verify tag created**

```bash
git tag -l | grep pre-refactor
```

Expected: `pre-refactor`

**Step 3: Verify current working tree is clean**

```bash
git status
```

Expected: `nothing to commit, working tree clean`

---

## Phase 1: Vite Migration (Keep JavaScript)

### Task 1.1: Install Vite dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install Vite and related packages**

```bash
cd frontend
npm install --save-dev vite @vitejs/plugin-react
npm install --save-dev @vitejs/plugin-react-swc
```

**Step 2: Verify installations**

```bash
cat package.json | grep -E "(vite|@vitejs/plugin-react)"
```

Expected:
```json
"vite": "^5.x.x"
"@vitejs/plugin-react": "^4.x.x"
```

### Task 1.2: Create Vite config

**Files:**
- Create: `frontend/vite.config.js`

**Step 1: Write Vite configuration**

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'build',
    sourcemap: true
  }
})
```

**Step 2: Move index.html to project root**

```bash
mv public/index.html index.html
```

**Step 3: Update index.html paths**

```html
<!DOCTYPE html>
<html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Lazy ASR</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
  </body>
</html>
```

**Step 4: Update index.js entry point**

Current `src/index.js` - remove React 18 createRoot wrapper if using React 19:
```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

**Step 5: Commit**

```bash
git add .
git commit -m "feat: add Vite configuration"
```

### Task 1.3: Update package.json scripts

**Files:**
- Modify: `frontend/package.json`

**Step 1: Replace CRA scripts with Vite scripts**

Replace `"scripts"` section with:
```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "lint": "eslint src --ext js,jsx",
  "test": "vitest"
}
```

**Step 2: Remove Browserslist config**

Remove `"browserslist"` section from package.json (not needed for Vite)

**Step 3: Commit**

```bash
git add package.json
git commit -m "chore: update scripts for Vite"
```

### Task 1.4: Verify Vite dev server works

**Files:**
- None (verification)

**Step 1: Start Vite dev server**

```bash
npm run dev
```

**Step 2: Verify application loads**

Expected: Server starts on http://localhost:3000, app renders correctly

**Step 3: Stop server and verify build**

```bash
npm run build
```

Expected: `build/` directory created successfully

**Step 4: Commit if any fixes needed**

```bash
git add .
git commit -m "fix: Vite dev server adjustments"
```

---

## Phase 2: TypeScript & Testing Infrastructure

### Task 2.1: Install TypeScript and testing dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install TypeScript and type packages**

```bash
npm install --save-dev typescript @types/react @types/react-dom
npm install --save-dev -D vitest @vitest/ui @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
npm install --save-dev msw
```

**Step 2: Verify installations**

```bash
cat package.json | grep -E "(typescript|vitest|testing-library|msw)"
```

Expected: All packages listed in devDependencies

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "deps: add TypeScript and testing dependencies"
```

### Task 2.2: Create TypeScript configuration

**Files:**
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts` (replace .js)

**Step 1: Create tsconfig.json with allowJs for gradual migration**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },

    /* Allow JS for gradual migration */
    "allowJs": true
  },
  "include": ["src", "tests"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 2: Create tsconfig.node.json for Vite config**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

**Step 3: Rename vite.config.js to vite.config.ts**

```bash
mv vite.config.js vite.config.ts
```

Update content to:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'build',
    sourcemap: true
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    css: true
  }
})
```

**Step 4: Commit**

```bash
git add tsconfig.json tsconfig.node.json vite.config.ts
git commit -m "feat: add TypeScript configuration"
```

### Task 2.3: Create Vitest setup and utilities

**Files:**
- Create: `frontend/tests/setup.ts`
- Create: `frontend/tests/mocks/handlers.ts`
- Create: `frontend/tests/utils/test-utils.tsx`

**Step 1: Create test setup file**

```typescript
// tests/setup.ts
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
```

**Step 2: Create MSW handlers for API mocking**

```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Mock submit files endpoint
  http.post('/api/submit', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      success: true,
      results: []
    })
  }),

  // Mock scan path endpoint
  http.post('/api/scan', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      success: true,
      files: []
    })
  }),

  // Mock get plugins endpoint
  http.get('/api/plugins', () => {
    return HttpResponse.json({
      plugins: ['whisper', 'faster-whisper', 'sherpa-onnx']
    })
  })
]
```

**Step 3: Create test utilities**

```typescript
// tests/utils/test-utils.tsx
import { ReactElement } from 'react'
import { render } from '@testing-library/react'
import { ConfigProvider } from '../path/to/ConfigContext' // Will update after migration

export function renderWithProviders(ui: ReactElement) {
  return render(ui, {
    wrapper: ({ children }) => (
      <ConfigProvider>{children}</ConfigProvider>
    )
  })
}
```

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: add Vitest setup and MSW handlers"
```

### Task 2.4: Verify test infrastructure works

**Files:**
- Create: `frontend/tests/example.test.ts`

**Step 1: Create example test**

```typescript
import { describe, it, expect } from 'vitest'

describe('Example test', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
})
```

**Step 2: Run Vitest**

```bash
npm run test
```

Expected: Tests pass

**Step 3: Commit**

```bash
git add tests/example.test.ts
git commit -m "test: add example test"
```

---

## Phase 3: Migrate Utils (TDD)

### Task 3.1: Create type definitions file

**Files:**
- Create: `frontend/src/types/index.ts`

**Step 1: Create core type definitions**

```typescript
// src/types/index.ts

/** ASR configuration options */
export interface ASRConfig {
  method: string
  language: string
  apiUrl?: string
  apiKey?: string
  model?: string
}

/** VAD (Voice Activity Detection) configuration */
export interface VADConfig {
  outputFormats: OutputFormat[]
  minSpeechDuration: number
  minSilenceDuration: number
  maxLineLength?: number
  maxLineWidth?: number
}

/** Supported output formats */
export type OutputFormat = 'srt' | 'vtt' | 'txt' | 'json' | 'ass'

/** Path scanner configuration */
export interface ScannerConfig {
  maxFiles: number
  recursive: boolean
  filePatterns: string[]
}

/** File processing result */
export interface ProcessResult {
  success: boolean
  filePath: string
  outputFiles: string[]
  duration?: number
  error?: string
}

/** API error response */
export interface ApiError {
  message: string
  code?: string
  details?: unknown
}

/** Global configuration state */
export interface ConfigState {
  asr: ASRConfig
  vad: VADConfig
  scanner: ScannerConfig
  isProcessing: boolean
}

/** Available plugin info */
export interface PluginInfo {
  name: string
  displayName: string
  supportedLanguages: string[]
}
```

**Step 2: Commit**

```bash
git add src/types/index.ts
git commit -m "feat(types): add core type definitions"
```

### Task 3.2: Migrate formatters.ts with tests

**Files:**
- Create: `frontend/src/utils/formatters.spec.ts`
- Modify: `frontend/src/utils/formatters.js` → `frontend/src/utils/formatters.ts`

**Step 1: Write tests first (TDD)**

Read current `src/utils/formatters.js` to understand functions:
```bash
cat src/utils/formatters.js
```

Create test file `src/utils/formatters.spec.ts`:
```typescript
// src/utils/formatters.spec.ts
import { describe, it, expect } from 'vitest'
import { formatDuration, formatFileSize, formatDate } from './formatters'

describe('formatDuration', () => {
  it('should format milliseconds as HH:MM:SS', () => {
    expect(formatDuration(0)).toBe('00:00:00')
    expect(formatDuration(1000)).toBe('00:00:01')
    expect(formatDuration(65000)).toBe('00:01:05')
    expect(formatDuration(3661000)).toBe('01:01:01')
  })

  it('should handle edge cases', () => {
    expect(formatDuration(-1)).toBe('00:00:00')
    expect(formatDuration(NaN)).toBe('00:00:00')
  })
})

describe('formatFileSize', () => {
  it('should format bytes in human-readable format', () => {
    expect(formatFileSize(0)).toBe('0 B')
    expect(formatFileSize(1024)).toBe('1 KB')
    expect(formatFileSize(1024 * 1024)).toBe('1 MB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
  })

  it('should handle edge cases', () => {
    expect(formatFileSize(-1)).toBe('0 B')
    expect(formatFileSize(NaN)).toBe('0 B')
  })
})

describe('formatDate', () => {
  it('should format date timestamp', () => {
    const timestamp = new Date('2024-01-15T10:30:00').getTime()
    const result = formatDate(timestamp)
    expect(result).toContain('2024')
  })

  it('should handle invalid dates', () => {
    expect(formatDate(NaN)).toBe('Invalid Date')
    expect(formatDate(-1)).toBe('Invalid Date')
  })
})
```

**Step 2: Run tests - should fail (file still .js)**

```bash
npm run test -- src/utils/formatters.spec.ts
```

Expected: Fail or cannot import

**Step 3: Migrate formatters.js to TypeScript**

```bash
mv src/utils/formatters.js src/utils/formatters.ts
```

Add types to functions:
```typescript
// src/utils/formatters.ts
import type { ProcessResult } from '../types'

/** Format duration in milliseconds to HH:MM:SS */
export function formatDuration(ms: number): string {
  if (typeof ms !== 'number' || ms < 0 || isNaN(ms)) {
    return '00:00:00'
  }

  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  return [hours, minutes, secs]
    .map(v => v.toString().padStart(2, '0'))
    .join(':')
}

/** Format file size in bytes to human-readable string */
export function formatFileSize(bytes: number): string {
  if (typeof bytes !== 'number' || bytes < 0 || isNaN(bytes)) {
    return '0 B'
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  // Format: use decimal for KB/MB/GB, whole for bytes
  if (unitIndex === 0) {
    return `${Math.round(size)} ${units[unitIndex]}`
  }

  return `${size.toFixed(size < 10 ? 1 : 0)} ${units[unitIndex]}`
}

/** Format timestamp to localized date string */
export function formatDate(timestamp: number): string {
  if (typeof timestamp !== 'number' || isNaN(timestamp) || timestamp < 0) {
    return 'Invalid Date'
  }

  const date = new Date(timestamp)
  if (isNaN(date.getTime())) {
    return 'Invalid Date'
  }

  return date.toLocaleString()
}
```

**Step 4: Run tests - should pass**

```bash
npm run test -- src/utils/formatters.spec.ts
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add src/utils/formatters.ts src/utils/formatters.spec.ts
git commit -m "refactor(utils): migrate formatters to TypeScript with tests"
```

### Task 3.3: Migrate errorHandler.ts with tests

**Files:**
- Create: `frontend/src/utils/errorHandler.spec.ts`
- Modify: `frontend/src/utils/errorHandler.js` → `frontend/src/utils/errorHandler.ts`

**Step 1: Read current error handler**

```bash
cat src/utils/errorHandler.js
```

**Step 2: Write tests first**

Create `src/utils/errorHandler.spec.ts`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { handleError, getErrorMessage } from './errorHandler'

describe('getErrorMessage', () => {
  it('should extract message from Error object', () => {
    const error = new Error('Test error')
    expect(getErrorMessage(error)).toBe('Test error')
  })

  it('should handle string errors', () => {
    expect(getErrorMessage('String error')).toBe('String error')
  })

  it('should handle unknown errors', () => {
    expect(getErrorMessage(null)).toBe('Unknown error')
    expect(getErrorMessage(undefined)).toBe('Unknown error')
  })

  it('should handle objects with message property', () => {
    expect(getErrorMessage({ message: 'Object error' })).toBe('Object error')
  })
})

describe('handleError', () => {
  it('should log error to console', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    handleError(new Error('Test error'))
    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('should return formatted error message', () => {
    const result = handleError(new Error('Test error'), 'Operation failed')
    expect(result).toContain('Operation failed')
    expect(result).toContain('Test error')
  })
})
```

**Step 3: Migrate errorHandler to TypeScript**

```bash
mv src/utils/errorHandler.js src/utils/errorHandler.ts
```

```typescript
// src/utils/errorHandler.ts
import type { ApiError } from '../types'

/** Custom ASR error class */
export class ASRError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: unknown
  ) {
    super(message)
    this.name = 'ASRError'
  }
}

/** Extract error message from various error types */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  if (typeof error === 'string') {
    return error
  }

  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message)
  }

  return 'Unknown error'
}

/** Handle and log errors consistently */
export function handleError(error: unknown, context?: string): string {
  const message = getErrorMessage(error)
  const fullMessage = context ? `${context}: ${message}` : message

  console.error(fullMessage, error)

  return fullMessage
}

/** Check if error is a network error */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.name === 'TypeError' ||
      error.message.includes('Network Error') ||
      error.message.includes('fetch')
    )
  }
  return false
}

/** Parse API error response */
export function parseApiError(data: unknown): ApiError {
  if (data && typeof data === 'object' && 'error' in data) {
    return {
      message: String(data.error),
      code: 'API_ERROR',
      details: data
    }
  }

  return {
    message: 'Unknown API error',
    code: 'UNKNOWN_ERROR'
  }
}
```

**Step 4: Run tests**

```bash
npm run test -- src/utils/errorHandler.spec.ts
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add src/utils/errorHandler.ts src/utils/errorHandler.spec.ts
git commit -m "refactor(utils): migrate errorHandler to TypeScript with tests"
```

### Task 3.4: Create constants/config.ts

**Files:**
- Modify: `frontend/src/constants/config.js` → `frontend/src/constants/config.ts`

**Step 1: Read current constants**

```bash
cat src/constants/config.js
```

**Step 2: Migrate to TypeScript**

```bash
mv src/constants/config.js src/constants/config.ts
```

```typescript
// src/constants/config.ts
import type { OutputFormat, PluginInfo } from '../types'

/** Default ASR language */
export const DEFAULT_LANGUAGE = 'auto'

/** Default output format */
export const DEFAULT_OUTPUT_FORMAT: OutputFormat = 'srt'

/** Minimum speech duration in ms */
export const MIN_SPEECH_DURATION = 100

/** Maximum speech duration in ms */
export const MAX_SPEECH_DURATION = 30000

/** Minimum silence duration in ms */
export const MIN_SILENCE_DURATION = 100

/** Maximum silence duration in ms */
export const MAX_SILENCE_DURATION = 10000

/** Maximum file scan count */
export const DEFAULT_MAX_FILES = 100

/** Available output formats */
export const OUTPUT_FORMATS: OutputFormat[] = ['srt', 'vtt', 'txt', 'json', 'ass']

/** Supported languages */
export const SUPPORTED_LANGUAGES = [
  { code: 'auto', name: 'Auto Detect' },
  { code: 'zh', name: 'Chinese' },
  { code: 'en', name: 'English' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'yue', name: 'Cantonese' }
] as const

/** API endpoints */
export const API_ENDPOINTS = {
  SUBMIT: '/api/submit',
  SCAN: '/api/scan',
  PLUGINS: '/api/plugins',
  STATUS: '/api/status'
} as const

/** File size limits */
export const FILE_SIZE_LIMITS = {
  MAX_SINGLE_FILE: 500 * 1024 * 1024, // 500MB
  MAX_TOTAL_SIZE: 5 * 1024 * 1024 * 1024 // 5GB
} as const
```

**Step 3: Commit**

```bash
git add src/constants/config.ts
git commit -m "refactor(constants): migrate config to TypeScript"
```

---

## Phase 4: Migrate Services

### Task 4.1: Migrate services/api.ts with tests

**Files:**
- Create: `frontend/src/services/api.spec.ts`
- Modify: `frontend/src/services/api.js` → `frontend/src/services/api.ts`

**Step 1: Read current API service**

```bash
cat src/services/api.js
```

**Step 2: Write tests for API functions**

Create `src/services/api.spec.ts`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { submitFiles, scanPath, getPlugins, checkStatus } from './api'
import type { ConfigState } from '../types'

const mockServer = setupServer(
  http.post('/api/submit', () => HttpResponse.json({ success: true, results: [] })),
  http.post('/api/scan', () => HttpResponse.json({ success: true, files: [] })),
  http.get('/api/plugins', () => HttpResponse.json({ plugins: ['whisper'] })),
  http.get('/api/status/:id', () => HttpResponse.json({ status: 'completed' }))
)

describe('API Service', () => {
  beforeEach(() => {
    mockServer.listen()
  })

  it('should submit files for processing', async () => {
    const files = [new File(['content'], 'test.mp3', { type: 'audio/mpeg' })]
    const config = {} as ConfigState

    const result = await submitFiles(files, config)
    expect(result).toBeDefined()
  })

  it('should scan path for files', async () => {
    const result = await scanPath('/path/to/dir', { maxFiles: 100, recursive: true, filePatterns: [] })
    expect(result).toEqual([])
  })

  it('should fetch available plugins', async () => {
    const plugins = await getPlugins()
    expect(plugins).toContain('whisper')
  })
})
```

**Step 3: Migrate API service to TypeScript**

```bash
mv src/services/api.js src/services/api.ts
```

Add types:
```typescript
// src/services/api.ts
import axios from 'axios'
import type { ConfigState, ProcessResult, PluginInfo } from '../types'
import { API_ENDPOINTS } from '../constants/config'
import { handleError, isNetworkError } from '../utils/errorHandler'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/** Submit files for ASR processing */
export async function submitFiles(
  files: File[],
  config: ConfigState
): Promise<ProcessResult[]> {
  try {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('config', JSON.stringify(config))

    const response = await apiClient.post(API_ENDPOINTS.SUBMIT, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    return response.data.results || []
  } catch (error) {
    if (isNetworkError(error)) {
      throw new Error('Network connection failed. Please check your connection.')
    }
    throw handleError(error, 'Failed to submit files')
  }
}

/** Scan directory for audio files */
export async function scanPath(
  path: string,
  options: { maxFiles: number; recursive: boolean; filePatterns: string[] }
): Promise<string[]> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.SCAN, {
      path,
      maxFiles: options.maxFiles,
      recursive: options.recursive,
      filePatterns: options.filePatterns
    })

    return response.data.files || []
  } catch (error) {
    throw handleError(error, 'Failed to scan path')
  }
}

/** Get available ASR plugins */
export async function getPlugins(): Promise<PluginInfo[]> {
  try {
    const response = await apiClient.get(API_ENDPOINTS.PLUGINS)
    return response.data.plugins || []
  } catch (error) {
    throw handleError(error, 'Failed to fetch plugins')
  }
}

/** Check processing status */
export async function checkStatus(taskId: string): Promise<{ status: string; progress: number }> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.STATUS}/${taskId}`)
    return response.data
  } catch (error) {
    throw handleError(error, 'Failed to check status')
  }
}
```

**Step 4: Run tests**

```bash
npm run test -- src/services/api.spec.ts
```

**Step 5: Commit**

```bash
git add src/services/api.ts src/services/api.spec.ts
git commit -m "refactor(services): migrate API service to TypeScript with tests"
```

---

## Phase 5: Migrate Context & Hooks

### Task 5.1: Migrate ConfigContext to TypeScript

**Files:**
- Create: `frontend/src/context/ConfigContext.spec.tsx`
- Modify: `frontend/src/context/ConfigContext.js` → `frontend/src/context/ConfigContext.tsx`

**Step 1: Read current context**

```bash
cat src/context/ConfigContext.js
```

**Step 2: Create type definitions for Context**

```typescript
// src/context/types.ts
import type { ConfigState, ASRConfig, VADConfig, ScannerConfig } from '../types'

/** Context action types */
export type ConfigAction =
  | { type: 'SET_ASR_METHOD'; payload: string }
  | { type: 'SET_LANGUAGE'; payload: string }
  | { type: 'SET_API_URL'; payload: string }
  | { type: 'SET_API_KEY'; payload: string }
  | { type: 'SET_MODEL'; payload: string }
  | { type: 'SET_OUTPUT_FORMATS'; payload: string[] }
  | { type: 'SET_MIN_SPEECH_DURATION'; payload: number }
  | { type: 'SET_MIN_SILENCE_DURATION'; payload: number }
  | { type: 'SET_MAX_FILES'; payload: number }
  | { type: 'SET_RECURSIVE'; payload: boolean }
  | { type: 'START_PROCESSING' }
  | { type: 'FINISH_PROCESSING' }
  | { type: 'RESET_CONFIG' }

export interface ConfigContextType {
  state: ConfigState
  dispatch: React.Dispatch<ConfigAction>
}
```

**Step 3: Migrate Context to TypeScript**

```bash
mv src/context/ConfigContext.js src/context/ConfigContext.tsx
```

```typescript
// src/context/ConfigContext.tsx
import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import type { ConfigState, ASRConfig, VADConfig, ScannerConfig } from '../types'
import type { ConfigAction, ConfigContextType } from './types'
import { DEFAULT_LANGUAGE, DEFAULT_OUTPUT_FORMAT } from '../constants/config'

const initialState: ConfigState = {
  asr: {
    method: '',
    language: DEFAULT_LANGUAGE,
    apiUrl: '',
    apiKey: '',
    model: ''
  },
  vad: {
    outputFormats: [DEFAULT_OUTPUT_FORMAT],
    minSpeechDuration: 500,
    minSilenceDuration: 500
  },
  scanner: {
    maxFiles: 100,
    recursive: true,
    filePatterns: ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.ogg', '*.webm']
  },
  isProcessing: false
}

function configReducer(state: ConfigState, action: ConfigAction): ConfigState {
  switch (action.type) {
    case 'SET_ASR_METHOD':
      return { ...state, asr: { ...state.asr, method: action.payload } }

    case 'SET_LANGUAGE':
      return { ...state, asr: { ...state.asr, language: action.payload } }

    case 'SET_API_URL':
      return { ...state, asr: { ...state.asr, apiUrl: action.payload } }

    case 'SET_API_KEY':
      return { ...state, asr: { ...state.asr, apiKey: action.payload } }

    case 'SET_MODEL':
      return { ...state, asr: { ...state.asr, model: action.payload } }

    case 'SET_OUTPUT_FORMATS':
      return { ...state, vad: { ...state.vad, outputFormats: action.payload } }

    case 'SET_MIN_SPEECH_DURATION':
      return { ...state, vad: { ...state.vad, minSpeechDuration: action.payload } }

    case 'SET_MIN_SILENCE_DURATION':
      return { ...state, vad: { ...state.vad, minSilenceDuration: action.payload } }

    case 'SET_MAX_FILES':
      return { ...state, scanner: { ...state.scanner, maxFiles: action.payload } }

    case 'SET_RECURSIVE':
      return { ...state, scanner: { ...state.scanner, recursive: action.payload } }

    case 'START_PROCESSING':
      return { ...state, isProcessing: true }

    case 'FINISH_PROCESSING':
      return { ...state, isProcessing: false }

    case 'RESET_CONFIG':
      return initialState

    default:
      return state
  }
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined)

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(configReducer, initialState)

  return (
    <ConfigContext.Provider value={{ state, dispatch }}>
      {children}
    </ConfigContext.Provider>
  )
}

export function useConfig(): ConfigContextType {
  const context = useContext(ConfigContext)
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider')
  }
  return context
}
```

**Step 4: Commit**

```bash
git add src/context/ConfigContext.tsx src/context/types.ts
git commit -m "refactor(context): migrate ConfigContext to TypeScript"
```

### Task 5.2: Migrate useASRProcessing hook

**Files:**
- Modify: `frontend/src/hooks/useASRProcessing.js` → `frontend/src/hooks/useASRProcessing.ts`

**Step 1: Read current hook**

```bash
cat src/hooks/useASRProcessing.js
```

**Step 2: Migrate to TypeScript**

```bash
mv src/hooks/useASRProcessing.js src/hooks/useASRProcessing.ts
```

```typescript
// src/hooks/useASRProcessing.ts
import { useState, useCallback } from 'react'
import type { ConfigState, ProcessResult } from '../types'
import { submitFiles } from '../services/api'
import { useConfig } from '../context/ConfigContext'
import { handleError } from '../utils/errorHandler'

export interface UseASRProcessingResult {
  processFiles: (files: File[]) => Promise<ProcessResult[]>
  isProcessing: boolean
  error: string | null
  clearError: () => void
}

export function useASRProcessing(): UseASRProcessingResult {
  const { state: config } = useConfig()
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const processFiles = useCallback(async (files: File[]): Promise<ProcessResult[]> => {
    setIsProcessing(true)
    setError(null)

    try {
      const results = await submitFiles(files, config)
      return results
    } catch (err) {
      const errorMessage = handleError(err, 'Processing failed')
      setError(errorMessage)
      return []
    } finally {
      setIsProcessing(false)
    }
  }, [config])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    processFiles,
    isProcessing,
    error,
    clearError
  }
}
```

**Step 3: Commit**

```bash
git add src/hooks/useASRProcessing.ts
git commit -m "refactor(hooks): migrate useASRProcessing to TypeScript"
```

---

## Phase 6: Migrate Components (Simple to Complex)

### Task 6.1: Migrate Header component

**Files:**
- Create: `frontend/src/components/Header.spec.tsx`
- Modify: `frontend/src/components/Header.js` → `frontend/src/components/Header.tsx`
- Modify: `frontend/src/components/Header.css` → `frontend/src/components/Header.module.css`

**Step 1: Read current component**

```bash
cat src/components/Header.js
```

**Step 2: Migrate to TypeScript**

```bash
mv src/components/Header.js src/components/Header.tsx
```

```typescript
// src/components/Header.tsx
import React from 'react'
import styles from './Header.module.css'

export interface HeaderProps {
  title?: string
  version?: string
}

export function Header({ title = 'Lazy ASR', version = '1.0.0' }: HeaderProps): React.ReactElement {
  return (
    <header className={styles.header}>
      <h1 className={styles.title}>{title}</h1>
      <span className={styles.version}>v{version}</span>
    </header>
  )
}
```

**Step 3: Convert CSS to CSS Module**

Create `src/components/Header.module.css`:
```css
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.version {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}
```

**Step 4: Commit**

```bash
git add src/components/Header.tsx src/components/Header.module.css
git rm src/components/Header.css  # if exists
git commit -m "refactor(header): migrate Header to TypeScript with CSS modules"
```

### Task 6.2: Migrate ProcessingIndicator component

**Files:**
- Modify: `frontend/src/components/ProcessingIndicator.js` → `frontend/src/components/ProcessingIndicator.tsx`

**Step 1: Read and migrate**

```bash
mv src/components/ProcessingIndicator.js src/components/ProcessingIndicator.tsx
```

```typescript
// src/components/ProcessingIndicator.tsx
import React from 'react'
import styles from './ProcessingIndicator.module.css'

export interface ProcessingIndicatorProps {
  isProcessing: boolean
  progress?: number
  message?: string
}

export function ProcessingIndicator({
  isProcessing,
  progress,
  message = 'Processing...'
}: ProcessingIndicatorProps): React.ReactElement | null {
  if (!isProcessing) return null

  return (
    <div className={styles.container}>
      <div className={styles.spinner} />
      {progress !== undefined && (
        <div className={styles.progress}>{progress.toFixed(0)}%</div>
      )}
      <div className={styles.message}>{message}</div>
    </div>
  )
}
```

**Step 5: Commit**

```bash
git add src/components/ProcessingIndicator.tsx
git commit -m "refactor(components): migrate ProcessingIndicator to TypeScript"
```

### Task 6.3: Migrate TabNavigation component

**Files:**
- Modify: `frontend/src/components/TabNavigation.js` → `frontend/src/components/TabNavigation.tsx`

**Step 1: Migrate**

```bash
mv src/components/TabNavigation.js src/components/TabNavigation.tsx
```

```typescript
// src/components/TabNavigation.tsx
import React from 'react'
import styles from './TabNavigation.module.css'

export type TabType = 'upload' | 'scanner' | 'monitor'

export interface Tab {
  id: TabType
  label: string
  icon: React.ComponentType<{ className?: string }>
}

export interface TabNavigationProps {
  tabs: Tab[]
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

export function TabNavigation({
  tabs,
  activeTab,
  onTabChange
}: TabNavigationProps): React.ReactElement {
  return (
    <nav className={styles.tabs}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          <tab.icon className={styles.icon} />
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/TabNavigation.tsx
git commit -m "refactor(components): migrate TabNavigation to TypeScript"
```

### Task 6.4: Migrate SubmitButtons component

**Files:**
- Modify: `frontend/src/components/SubmitButtons.js` → `frontend/src/components/SubmitButtons.tsx`

**Step 1: Migrate**

```bash
mv src/components/SubmitButtons.js src/components/SubmitButtons.tsx
```

```typescript
// src/components/SubmitButtons.tsx
import React from 'react'
import styles from './SubmitButtons.module.css'
import { Play, Upload } from 'lucide-react'

export interface SubmitButtonsProps {
  isProcessing: boolean
  hasFiles: boolean
  onStart: () => void
  onReset: () => void
}

export function SubmitButtons({
  isProcessing,
  hasFiles,
  onStart,
  onReset
}: SubmitButtonsProps): React.ReactElement {
  return (
    <div className={styles.container}>
      <button
        className={styles.primaryButton}
        onClick={onStart}
        disabled={!hasFiles || isProcessing}
      >
        <Play className={styles.icon} />
        {isProcessing ? 'Processing...' : 'Start Processing'}
      </button>
      <button
        className={styles.secondaryButton}
        onClick={onReset}
        disabled={isProcessing}
      >
        <Upload className={styles.icon} />
        Reset
      </button>
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/SubmitButtons.tsx
git commit -m "refactor(components): migrate SubmitButtons to TypeScript"
```

### Task 6.5: Migrate ResultDisplay component

**Files:**
- Modify: `frontend/src/components/ResultDisplay.js` → `frontend/src/components/ResultDisplay.tsx`

**Step 1: Migrate**

```bash
mv src/components/ResultDisplay.js src/components/ResultDisplay.tsx
```

```typescript
// src/components/ResultDisplay.tsx
import React from 'react'
import type { ProcessResult } from '../types'
import { formatFileSize, formatDate, formatDuration } from '../utils/formatters'
import { Download, FileText, AlertCircle } from 'lucide-react'
import styles from './ResultDisplay.module.css'

export interface ResultDisplayProps {
  results: ProcessResult[]
  onDownload?: (result: ProcessResult) => void
  onClear?: () => void
}

export function ResultDisplay({
  results,
  onDownload,
  onClear
}: ResultDisplayProps): React.ReactElement | null {
  if (results.length === 0) return null

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>Processing Results</h3>
        {onClear && (
          <button onClick={onClear} className={styles.clearButton}>
            Clear
          </button>
        )}
      </div>
      <div className={styles.results}>
        {results.map((result, index) => (
          <div
            key={index}
            className={`${styles.result} ${result.success ? styles.success : styles.error}`}
          >
            {result.success ? (
              <>
                <FileText className={styles.icon} />
                <div className={styles.info}>
                  <div className={styles.filePath}>{result.filePath}</div>
                  {result.duration && (
                    <div className={styles.meta}>
                      Duration: {formatDuration(result.duration)}
                    </div>
                  )}
                  {result.outputFiles.length > 0 && (
                    <div className={styles.outputs}>
                      {result.outputFiles.map((file, i) => (
                        <button
                          key={i}
                          onClick={() => onDownload?.(result)}
                          className={styles.downloadButton}
                        >
                          <Download className={styles.downloadIcon} />
                          {file}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <AlertCircle className={styles.errorIcon} />
                <div className={styles.info}>
                  <div className={styles.filePath}>{result.filePath}</div>
                  <div className={styles.errorMessage}>{result.error}</div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/ResultDisplay.tsx
git commit -m "refactor(components): migrate ResultDisplay to TypeScript"
```

### Task 6.6: Migrate ConfigPanel component

**Files:**
- Modify: `frontend/src/components/ConfigPanel.js` → `frontend/src/components/ConfigPanel.tsx`

**Step 1: Migrate**

```bash
mv src/components/ConfigPanel.js src/components/ConfigPanel.tsx
```

```typescript
// src/components/ConfigPanel.tsx
import React from 'react'
import { useConfig } from '../context/ConfigContext'
import { SUPPORTED_LANGUAGES, OUTPUT_FORMATS, MIN_SPEECH_DURATION, MAX_SPEECH_DURATION } from '../constants/config'
import styles from './ConfigPanel.module.css'

export interface ConfigPanelProps {
  className?: string
}

export function ConfigPanel({ className }: ConfigPanelProps): React.ReactElement {
  const { state, dispatch } = useConfig()

  return (
    <div className={`${styles.panel} ${className || ''}`}>
      {/* ASR Config Section */}
      <section className={styles.section}>
        <h3>ASR Configuration</h3>
        <div className={styles.field}>
          <label>Language</label>
          <select
            value={state.asr.language}
            onChange={e => dispatch({ type: 'SET_LANGUAGE', payload: e.target.value })}
          >
            {SUPPORTED_LANGUAGES.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </section>

      {/* VAD Config Section */}
      <section className={styles.section}>
        <h3>VAD Configuration</h3>
        <div className={styles.field}>
          <label>Output Formats</label>
          <div className={styles.checkboxGroup}>
            {OUTPUT_FORMATS.map(format => (
              <label key={format} className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={state.vad.outputFormats.includes(format)}
                  onChange={e => {
                    const formats = e.target.checked
                      ? [...state.vad.outputFormats, format]
                      : state.vad.outputFormats.filter(f => f !== format)
                    dispatch({ type: 'SET_OUTPUT_FORMATS', payload: formats })
                  }}
                />
                {format.toUpperCase()}
              </label>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/ConfigPanel.tsx
git commit -m "refactor(components): migrate ConfigPanel to TypeScript"
```

### Task 6.7: Migrate FileUpload component

**Files:**
- Modify: `frontend/src/components/FileUpload.js` → `frontend/src/components/FileUpload.tsx`

**Step 1: Migrate**

```bash
mv src/components/FileUpload.js src/components/FileUpload.tsx
```

```typescript
// src/components/FileUpload.tsx
import React, { useCallback, useState } from 'react'
import { Upload as UploadIcon, File, X } from 'lucide-react'
import type { ProcessResult } from '../types'
import { formatFileSize } from '../utils/formatters'
import styles from './FileUpload.module.css'

export interface FileUploadProps {
  onFilesSelected: (files: File[]) => void
  results?: ProcessResult[]
  disabled?: boolean
  acceptedTypes?: string
}

export function FileUpload({
  onFilesSelected,
  results = [],
  disabled = false,
  acceptedTypes = 'audio/*,video/*'
}: FileUploadProps): React.ReactElement {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    setSelectedFiles(files)
    onFilesSelected(files)
  }, [onFilesSelected])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setSelectedFiles(files)
    onFilesSelected(files)
  }, [onFilesSelected])

  const removeFile = useCallback((index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }, [selectedFiles, onFilesSelected])

  return (
    <div className={styles.container}>
      <div
        className={`${styles.dropZone} ${dragActive ? styles.dragActive : ''} ${disabled ? styles.disabled : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept={acceptedTypes}
          onChange={handleInputChange}
          className={styles.input}
          disabled={disabled}
        />
        <UploadIcon className={styles.icon} />
        <p>Drag & drop files here or click to browse</p>
        <span className={styles.hint}>Supported: MP3, WAV, M4A, FLAC, OGG, WebM</span>
      </div>

      {selectedFiles.length > 0 && (
        <div className={styles.fileList}>
          {selectedFiles.map((file, index) => (
            <div key={index} className={styles.fileItem}>
              <File className={styles.fileIcon} />
              <div className={styles.fileInfo}>
                <div className={styles.fileName}>{file.name}</div>
                <div className={styles.fileSize}>{formatFileSize(file.size)}</div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className={styles.removeButton}
                disabled={disabled}
              >
                <X />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/FileUpload.tsx
git commit -m "refactor(components): migrate FileUpload to TypeScript"
```

### Task 6.8: Migrate FileUploadTab component

**Files:**
- Modify: `frontend/src/components/FileUploadTab.js` → `frontend/src/components/FileUploadTab.tsx`

**Step 1: Migrate**

```bash
mv src/components/FileUploadTab.js src/components/FileUploadTab.tsx
```

```typescript
// src/components/FileUploadTab.tsx
import React from 'react'
import { useConfig } from '../context/ConfigContext'
import { useASRProcessing } from '../hooks/useASRProcessing'
import { FileUpload } from './FileUpload'
import { ConfigPanel } from './ConfigPanel'
import { SubmitButtons } from './SubmitButtons'
import { ResultDisplay } from './ResultDisplay'
import { ProcessingIndicator } from './ProcessingIndicator'
import type { ProcessResult } from '../types'
import styles from './FileUploadTab.module.css'

export interface FileUploadTabProps {
  className?: string
}

export function FileUploadTab({ className }: FileUploadTabProps): React.ReactElement {
  const { state, dispatch } = useConfig()
  const { processFiles, isProcessing, error, clearError } = useASRProcessing()
  const [files, setFiles] = React.useState<File[]>([])
  const [results, setResults] = React.useState<ProcessResult[]>([])

  const handleStart = async () => {
    const processingResults = await processFiles(files)
    setResults(processingResults)
    if (processingResults.length > 0) {
      dispatch({ type: 'FINISH_PROCESSING' })
    }
  }

  const handleReset = () => {
    setFiles([])
    setResults([])
    clearError()
  }

  return (
    <div className={`${styles.tab} ${className || ''}`}>
      <div className={styles.mainContent}>
        <FileUpload
          onFilesSelected={setFiles}
          results={results}
          disabled={isProcessing}
        />
        <ConfigPanel />
      </div>

      <SubmitButtons
        isProcessing={isProcessing}
        hasFiles={files.length > 0}
        onStart={handleStart}
        onReset={handleReset}
      />

      {error && <div className={styles.error}>{error}</div>}

      <ProcessingIndicator isProcessing={isProcessing} />

      {results.length > 0 && (
        <ResultDisplay
          results={results}
          onClear={handleReset}
        />
      )}
    </div>
  )
}
```

**Step 2: Commit**

```bash
git add src/components/FileUploadTab.tsx
git commit -m "refactor(components): migrate FileUploadTab to TypeScript"
```

### Task 6.9: Migrate remaining components (PathScanner, MonitorManager, FolderSelector)

**Files:**
- Modify: `frontend/src/components/PathScanner.js` → `frontend/src/components/PathScanner.tsx`
- Modify: `frontend/src/components/MonitorManager.js` → `frontend/src/components/MonitorManager.tsx`
- Modify: `frontend/src/components/FolderSelector.js` → `frontend/src/components/FolderSelector.tsx`

**Step 1: Migrate PathScanner**

```bash
mv src/components/PathScanner.js src/components/PathScanner.tsx
```

**Step 2: Migrate MonitorManager**

```bash
mv src/components/MonitorManager.js src/components/MonitorManager.tsx
```

**Step 3: Migrate FolderSelector**

```bash
mv src/components/FolderSelector.js src/components/FolderSelector.tsx
```

**Step 4: Commit**

```bash
git add src/components/PathScanner.tsx src/components/MonitorManager.tsx src/components/FolderSelector.tsx
git commit -m "refactor(components): migrate remaining components to TypeScript"
```

### Task 6.10: Migrate App.js to App.tsx

**Files:**
- Modify: `frontend/src/App.js` → `frontend/src/App.tsx`

**Step 1: Read current App.js**

```bash
cat src/App.js
```

**Step 2: Migrate to TypeScript**

```bash
mv src/App.js src/App.tsx
mv src/index.js src/index.tsx
```

Update `src/index.tsx`:
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import './i18n'
import './index.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

Update `src/App.tsx`:
```typescript
import React, { useState } from 'react'
import { ConfigProvider } from './context/ConfigContext'
import { Header } from './components/Header'
import { TabNavigation, type TabType } from './components/TabNavigation'
import { FileUploadTab } from './components/FileUploadTab'
import { PathScanner } from './components/PathScanner'
import { MonitorManager } from './components/MonitorManager'
import { Upload as UploadIcon, FolderOpen, Activity } from 'lucide-react'
import './App.css'

const tabs = [
  { id: 'upload' as TabType, label: 'File Upload', icon: UploadIcon },
  { id: 'scanner' as TabType, label: 'Path Scanner', icon: FolderOpen },
  { id: 'monitor' as TabType, label: 'Monitor Manager', icon: Activity }
]

function AppContent(): React.ReactElement {
  const [activeTab, setActiveTab] = useState<TabType>('upload')

  return (
    <div className="app">
      <Header />
      <TabNavigation
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      <main className="main-content">
        {activeTab === 'upload' && <FileUploadTab />}
        {activeTab === 'scanner' && <PathScanner />}
        {activeTab === 'monitor' && <MonitorManager />}
      </main>
    </div>
  )
}

function App(): React.ReactElement {
  return (
    <ConfigProvider>
      <AppContent />
    </ConfigProvider>
  )
}

export default App
```

**Step 3: Commit**

```bash
git add src/App.tsx src/index.tsx
git commit -m "refactor(app): migrate App to TypeScript"
```

---

## Phase 7: CSS Migration & Cleanup

### Task 7.1: Create global styles from App.css

**Files:**
- Modify: `frontend/src/App.css`
- Create: `frontend/src/styles/global.css`

**Step 1: Extract global styles**

Create `src/styles/global.css` with design tokens and base styles:
```css
:root {
  /* Colors */
  --color-primary: #667eea;
  --color-secondary: #764ba2;
  --color-background: #0f0f1a;
  --color-surface: rgba(255, 255, 255, 0.05);
  --color-surface-hover: rgba(255, 255, 255, 0.1);
  --color-border: rgba(255, 255, 255, 0.1);
  --color-text: #ffffff;
  --color-text-secondary: rgba(255, 255, 255, 0.6);
  --color-text-muted: rgba(255, 255, 255, 0.4);
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-warning: #f59e0b;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Typography */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 2rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.3);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: var(--color-background);
  color: var(--color-text);
  line-height: 1.5;
  min-height: 100vh;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
```

**Step 2: Update App.css to only have app-specific styles**

```bash
# Remove most content from App.css, keep only .app specific styles
```

**Step 3: Update index.tsx to import global styles**

```typescript
import './styles/global.css'
```

**Step 4: Commit**

```bash
git add src/styles/global.css src/App.css src/index.tsx
git commit -m "refactor(styles): extract global styles and design tokens"
```

### Task 7.2: Update all component CSS to modules

**Files:**
- All component CSS files

**Step 1: For each remaining .css file, create .module.css version**

```bash
# Example for each component
mv src/components/[Component].css src/components/[Component].module.css
```

**Step 2: Update component imports**

```typescript
import styles from './ComponentName.module.css'
```

**Step 3: Update className usage to use styles object**

```typescript
// Before: className="header"
// After: className={styles.header}
```

**Step 4: Commit each component**

```bash
git add src/components/
git commit -m "refactor(styles): migrate remaining components to CSS modules"
```

### Task 7.3: Remove old CSS files

**Files:**
- Various old CSS files

**Step 1: Find and remove orphaned CSS files**

```bash
find src/components -name "*.css" -not -name "*.module.css"
```

**Step 2: Remove any found**

```bash
git rm src/components/orphaned.css
```

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: remove old CSS files after migration"
```

---

## Phase 8: Final Verification & Cleanup

### Task 8.1: Remove allowJs and enforce strict TypeScript

**Files:**
- Modify: `frontend/tsconfig.json`

**Step 1: Update tsconfig.json**

Remove `allowJs: true` from tsconfig.json to enforce full TypeScript:
```json
{
  "compilerOptions": {
    // ... other options
    "allowJs": false  // Changed from true
  }
}
```

**Step 2: Check for any remaining .js files**

```bash
find src -name "*.js" -not -path "*/node_modules/*"
```

**Step 3: Verify no type errors**

```bash
npx tsc --noEmit
```

Expected: No errors

**Step 4: Commit**

```bash
git add tsconfig.json
git commit -m "feat(types): enforce strict TypeScript mode"
```

### Task 8.2: Run full test suite

**Files:**
- None (verification)

**Step 1: Run all tests**

```bash
npm run test -- --run
```

Expected: All tests pass

**Step 2: Check test coverage**

```bash
npm run test -- --coverage
```

Expected: Coverage report generated

**Step 3: Fix any failing tests**

```bash
# If tests fail, fix and commit
git add .
git commit -m "test: fix failing tests"
```

### Task 8.3: Verify production build

**Files:**
- None (verification)

**Step 1: Run production build**

```bash
npm run build
```

Expected: Clean build with no errors

**Step 2: Test build output locally**

```bash
npm run preview
```

Expected: Application runs correctly

**Step 3: Check bundle size**

```bash
ls -lh build/assets/
```

Expected: Reasonable bundle sizes

**Step 4: Commit if any fixes needed**

```bash
git add .
git commit -m "fix: production build adjustments"
```

### Task 8.4: Update ESLint configuration for TypeScript

**Files:**
- Create: `frontend/.eslintrc.cjs`

**Step 1: Create ESLint config**

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended'
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }]
  }
}
```

**Step 2: Install ESLint dependencies**

```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react-refresh
```

**Step 3: Run ESLint**

```bash
npm run lint
```

**Step 4: Fix any issues**

```bash
npm run lint -- --fix
```

**Step 5: Commit**

```bash
git add .eslintrc.cjs package.json package-lock.json
git commit -m "chore: add TypeScript ESLint configuration"
```

### Task 8.5: Final cleanup and documentation

**Files:**
- Modify: `frontend/README.md` (if exists)
- Create: `frontend/DEVELOPMENT.md`

**Step 1: Update documentation**

Create `DEVELOPMENT.md`:
```markdown
# Development Guide

## Tech Stack
- React 19 with TypeScript
- Vite for build tooling
- Vitest for testing
- CSS Modules for styling

## Development

\`\`\`bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
\`\`\`

## Project Structure

\`\`\`
src/
├── components/     # React components with .module.css
├── context/        # React Context for state
├── hooks/          # Custom hooks
├── services/       # API services
├── utils/          # Utility functions
├── types/          # TypeScript type definitions
├── constants/      # App constants
└── styles/         # Global styles
\`\`\`

## Testing

\`\`\`bash
# Run all tests
npm run test

# Run with UI
npm run test -- --ui

# Coverage
npm run test -- --coverage
\`\`\`
```

**Step 2: Remove any unused dependencies**

```bash
npm uninstall react-scripts
```

**Step 3: Final verification**

```bash
npm run build
npm run test -- --run
```

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: final cleanup and documentation"
```

---

## Phase 9: Completion

### Task 9.1: Create completion summary

**Files:**
- None (summary)

**Step 1: Verify all tasks complete**

```bash
# Check no .js files remain in src
find src -name "*.js" -not -path "*/node_modules/*"

# Verify TypeScript compiles
npx tsc --noEmit

# Verify tests pass
npm run test -- --run

# Verify build
npm run build
```

**Step 2: Create git tag for completion**

```bash
git tag -a frontend-refactor-complete -m "Frontend modernization complete"
git push origin frontend-refactor-complete
```

**Step 3: Summary of changes**

- ✅ Migrated from CRA to Vite
- ✅ Migrated all .js files to TypeScript
- ✅ Added Vitest testing infrastructure
- ✅ Migrated to CSS Modules
- ✅ Added type definitions
- ✅ Configured ESLint for TypeScript

**Step 4: Celebrate!**

```bash
echo "Frontend modernization complete! 🎉"
```

---

## Migration Checklist

Use this checklist to track progress:

### Phase 0: Pre-work
- [ ] Create baseline git tag
- [ ] Verify working tree is clean

### Phase 1: Vite Migration
- [ ] Install Vite dependencies
- [ ] Create vite.config.js/ts
- [ ] Move and update index.html
- [ ] Update package.json scripts
- [ ] Verify dev server works

### Phase 2: TypeScript & Testing
- [ ] Install TypeScript and testing deps
- [ ] Create tsconfig.json
- [ ] Create Vitest setup
- [ ] Create MSW handlers
- [ ] Verify tests work

### Phase 3: Utils Migration
- [ ] Create types/index.ts
- [ ] Migrate formatters.ts + tests
- [ ] Migrate errorHandler.ts + tests
- [ ] Migrate constants/config.ts

### Phase 4: Services Migration
- [ ] Migrate api.ts + tests

### Phase 5: Context & Hooks
- [ ] Migrate ConfigContext
- [ ] Migrate useASRProcessing

### Phase 6: Components Migration
- [ ] Migrate Header
- [ ] Migrate ProcessingIndicator
- [ ] Migrate TabNavigation
- [ ] Migrate SubmitButtons
- [ ] Migrate ResultDisplay
- [ ] Migrate ConfigPanel
- [ ] Migrate FileUpload
- [ ] Migrate FileUploadTab
- [ ] Migrate PathScanner
- [ ] Migrate MonitorManager
- [ ] Migrate FolderSelector
- [ ] Migrate App.tsx
- [ ] Migrate index.tsx

### Phase 7: CSS Migration
- [ ] Extract global styles
- [ ] Migrate all components to CSS modules
- [ ] Remove old CSS files

### Phase 8: Final Verification
- [ ] Remove allowJs from tsconfig
- [ ] Run full test suite
- [ ] Verify production build
- [ ] Update ESLint config
- [ ] Update documentation

### Phase 9: Completion
- [ ] Create completion tag
- [ ] Verify all changes

---

## Rollback Plan

If anything goes wrong:

```bash
# Reset to pre-refactor state
git reset --hard pre-refactor

# Or use the tag
git checkout pre-refactor -b recovery-branch
```

---

## Notes for Implementation

1. **Commit frequently** - Each task should end with a commit
2. **Test after each phase** - Run `npm run test -- --run` after each phase
3. **Keep app working** - The app should remain functional throughout
4. **Use git stash** - If you need to test something experimental
5. **Document deviations** - If you need to deviate from this plan, note why

---

**Plan created:** 2025-01-22
**Estimated complexity:** Medium-High
**Risk level:** Medium (mitigated by gradual approach and backups)
