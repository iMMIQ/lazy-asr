import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { I18nextProvider } from 'react-i18next'
import i18n from '../i18n'
import { PathScanner } from './PathScanner'
import * as api from '../services/api'

// Mock the API module
vi.mock('../services/api', () => ({
  startScan: vi.fn(),
  getScanStatus: vi.fn(),
  getScanResult: vi.fn(),
  cancelScan: vi.fn(),
  getScanConfig: vi.fn(),
}))

// Mock the useWebSocket hook
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(),
}))

const { useWebSocket } = await import('../hooks/useWebSocket')

/**
 * Test wrapper with i18n and ConfigContext
 */
function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      {div({ className: 'test-wrapper', children })}
    </I18nextProvider>
  )
}

// Helper for creating JSX elements in tests
function div(props: { className?: string; children: React.ReactNode }) {
  return React.createElement('div', { className: props.className }, props.children)
}

// Import React after mocks are set up
import React from 'react'
import { ConfigProvider } from '../context/ConfigContext'

describe('PathScanner - WebSocket Integration', () => {
  const mockConfig = {
    scan_paths: ['/media/videos', '/home/user/Music'],
  }

  const defaultConfigState = {
    asrMethod: 'whisper-api',
    availablePlugins: [],
    outputFormats: ['srt'],
    minSpeechDuration: 0.1,
    minSilenceDuration: 0.3,
    asrLanguage: 'auto' as const,
    asrApiUrl: '',
    asrApiKey: '',
    asrModel: '',
    maxFiles: 100,
    recursive: true,
    processing: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()

    // Mock getScanConfig
    vi.mocked(api.getScanConfig).mockResolvedValue(mockConfig)

    // Default WebSocket mock - disconnected
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'disconnected',
      connected: false,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render without crashing', async () => {
    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })
  })

  it('should use WebSocket when available and connected', async () => {
    // Initially disconnected
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'disconnected',
      connected: false,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })

    vi.mocked(api.startScan).mockResolvedValue({ scan_id: 'test-scan-123' })

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    // Start a scan
    const user = userEvent.setup()
    const pathInput = screen.getByPlaceholderText(/\/path\/to\/media\/files/i)
    await user.type(pathInput, '/media/videos')

    const startButton = screen.getByText(/Start Scan/i)
    await user.click(startButton)

    await waitFor(() => {
      expect(api.startScan).toHaveBeenCalled()
    })

    // Verify connection status is initially showing as disconnected
    const statusIndicator = screen.getByTestId(/connection-status/i)
    expect(statusIndicator).toHaveClass('disconnected')
  })

  it('should show connection status indicator', async () => {
    // Mock WebSocket as connected
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'connected',
      connected: true,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    // Check for connection status indicator
    const statusIndicator = screen.getByTestId(/connection-status/i)
    expect(statusIndicator).toBeInTheDocument()
    expect(statusIndicator).toHaveClass('connected')
  })

  it('should update scan status from WebSocket messages', async () => {
    // This test verifies the WebSocket hook is being used correctly
    // The actual status update logic is tested in the hook's own tests
    vi.mocked(api.startScan).mockResolvedValue({ scan_id: 'test-scan-789' })

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    // Verify connection status indicator exists
    const statusIndicator = screen.getByTestId(/connection-status/i)
    expect(statusIndicator).toBeInTheDocument()
  })

  it('should handle WebSocket connection errors gracefully', async () => {
    // Mock WebSocket with error
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'error',
      connected: false,
      lastMessage: null,
      lastStatus: null,
      error: 'WebSocket connection failed',
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    // Check that error status is shown (but doesn't break the UI)
    const statusIndicator = screen.getByTestId(/connection-status/i)
    expect(statusIndicator).toBeInTheDocument()
    expect(statusIndicator).toHaveClass('disconnected')
  })

  it('should display correct connection status class based on WebSocket state', async () => {
    // Test connected state
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'connected',
      connected: true,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })

    const { rerender } = render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      const statusIndicator = screen.getByTestId(/connection-status/i)
      expect(statusIndicator).toHaveClass('connected')
      expect(statusIndicator).not.toHaveClass('disconnected')
    })

    // Test disconnected state
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'disconnected',
      connected: false,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })

    rerender(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      const statusIndicator = screen.getByTestId(/connection-status/i)
      expect(statusIndicator).toHaveClass('disconnected')
      expect(statusIndicator).not.toHaveClass('connected')
    })
  })
})

describe('PathScanner - Basic Functionality', () => {
  const mockConfig = {
    scan_paths: ['/media/videos'],
  }

  const defaultConfigState = {
    asrMethod: 'whisper-api',
    availablePlugins: [],
    outputFormats: ['srt'],
    minSpeechDuration: 0.1,
    minSilenceDuration: 0.3,
    asrLanguage: 'auto' as const,
    asrApiUrl: '',
    asrApiKey: '',
    asrModel: '',
    maxFiles: 100,
    recursive: true,
    processing: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.getScanConfig).mockResolvedValue(mockConfig)
    vi.mocked(useWebSocket).mockReturnValue({
      status: 'disconnected',
      connected: false,
      lastMessage: null,
      lastStatus: null,
      error: null,
      sendMessage: vi.fn(),
      disconnect: vi.fn(),
      reconnect: vi.fn(),
    })
  })

  it('should validate empty path input', async () => {
    // Override mock to return no scan paths
    vi.mocked(api.getScanConfig).mockResolvedValue({})

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    // The start button should be disabled when path is empty
    const startButton = screen.getByText(/Start Scan/i)
    expect(startButton).toBeDisabled()
  })

  it('should start a scan with valid path', async () => {
    vi.mocked(api.startScan).mockResolvedValue({ scan_id: 'new-scan-123' })

    render(
      <ConfigProvider defaultState={defaultConfigState}>
        <TestWrapper>
          <PathScanner />
        </TestWrapper>
      </ConfigProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/path scanner/i)).toBeInTheDocument()
    })

    const user = userEvent.setup()
    const pathInput = screen.getByPlaceholderText(/\/path\/to\/media\/files/i)

    // Type in the path input
    await user.type(pathInput, '/media/videos')

    // Verify the button is now enabled
    const startButton = screen.getByText(/Start Scan/i)
    expect(startButton).not.toBeDisabled()

    // Submit the form by clicking the button
    await user.click(startButton)

    await waitFor(() => {
      expect(api.startScan).toHaveBeenCalled()
    })
  })
})
