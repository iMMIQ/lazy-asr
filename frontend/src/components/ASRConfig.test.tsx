import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../i18n'
import { ASRConfig } from './ASRConfig'
import type { ASRPlugin } from '../types'

/**
 * Test wrapper for i18n
 */
function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      {children}
    </I18nextProvider>
  )
}

/**
 * Bug fix verification: ASR service list shows display_name instead of plugin name
 *
 * Previously: availablePlugins was passed as string array (e.g., ['whisper-api']),
 * causing the component to display raw plugin names.
 *
 * After fix: availablePlugins is passed as ASRPlugin[] array, and the component
 * displays the user-friendly display_name field.
 */
describe('ASRConfig - Service list display', () => {
  const mockPlugins: ASRPlugin[] = [
    {
      name: 'whisper-api',
      display_name: 'Whisper API',
      description: 'Fast and accurate speech recognition',
      supported_languages: ['auto', 'zh', 'en'],
      requires_api_key: false,
      requires_api_url: true,
      model_parameter: 'model'
    },
    {
      name: 'qwen-asr',
      display_name: 'Qwen ASR',
      description: 'Alibaba Cloud ASR service',
      supported_languages: ['auto', 'zh', 'en'],
      requires_api_key: true,
      requires_api_url: false,
      model_parameter: 'model'
    }
  ]

  it('should display display_name instead of plugin name', () => {
    const handleChange = vi.fn()

    render(
      <TestWrapper>
        <ASRConfig
          asrMethod="whisper-api"
          availablePlugins={mockPlugins}
          outputFormats={['srt']}
          onMethodChange={handleChange}
          onFormatChange={vi.fn()}
          isProcessing={false}
        />
      </TestWrapper>
    )

    // Should show "Whisper API" not "whisper-api"
    expect(screen.getByText('Whisper API')).toBeInTheDocument()
    expect(screen.getByText('Qwen ASR')).toBeInTheDocument()

    // Should NOT show raw plugin names
    expect(screen.queryByText('whisper-api')).not.toBeInTheDocument()
    expect(screen.queryByText('qwen-asr')).not.toBeInTheDocument()
  })

  it('should use plugin.name as option value', () => {
    const handleChange = vi.fn()

    render(
      <TestWrapper>
        <ASRConfig
          asrMethod="whisper-api"
          availablePlugins={mockPlugins}
          outputFormats={['srt']}
          onMethodChange={handleChange}
          onFormatChange={vi.fn()}
          isProcessing={false}
        />
      </TestWrapper>
    )

    // Check that select element has the correct value (plugin.name, not display_name)
    const selectElement = screen.getByLabelText(/select asr service/i) as HTMLSelectElement
    expect(selectElement.value).toBe('whisper-api')

    // Check that options have correct values
    const options = selectElement.querySelectorAll('option')
    expect(options[0].value).toBe('whisper-api')
    expect(options[0].textContent).toBe('Whisper API')
    expect(options[1].value).toBe('qwen-asr')
    expect(options[1].textContent).toBe('Qwen ASR')
  })
})
