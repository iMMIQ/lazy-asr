import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../i18n'
import { ConfigPanel } from './ConfigPanel'
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

describe('ConfigPanel - Language options display', () => {
  const mockPlugins: ASRPlugin[] = [
    {
      name: 'faster-whisper',
      display_name: 'Faster Whisper',
      description: 'Fast and accurate speech recognition',
      supported_languages: ['auto', 'zh', 'en', 'ja'],
      requires_api_key: false,
      requires_api_url: true,
      model_parameter: 'model'
    }
  ]

  it('should display each language with its correct name (no duplicates)', () => {
    const handleChange = vi.fn()

    render(
      <TestWrapper>
        <ConfigPanel
          asrMethod="faster-whisper"
          availablePlugins={mockPlugins}
          outputFormats={['srt']}
          onMethodChange={handleChange}
          onFormatChange={vi.fn()}
          onAsrConfigChange={vi.fn()}
          showVadConfig={false}
          showAsrAdvancedConfig={false}
        />
      </TestWrapper>
    )

    // Get the language select element
    const languageSelect = screen.getByLabelText(/language:/i) as HTMLSelectElement
    const options = Array.from(languageSelect.querySelectorAll('option'))
    const optionTexts = options.map(opt => opt.textContent)

    // Check that we have the expected number of unique language names
    const uniqueTexts = new Set(optionTexts)

    // Should have exactly 4 unique languages: Auto Detect, Chinese, English, Japanese
    expect(uniqueTexts.size).toBe(4)

    // Count how many times "Japanese" appears - should be exactly 1
    const japaneseCount = optionTexts.filter(text => text === 'Japanese').length
    expect(japaneseCount).toBe(1)

    // Verify total unique options match total options (no duplicates)
    expect(uniqueTexts.size).toBe(optionTexts.length)
  })

  it('should display Japanese as "Japanese"', () => {
    const handleChange = vi.fn()

    render(
      <TestWrapper>
        <ConfigPanel
          asrMethod="faster-whisper"
          availablePlugins={mockPlugins}
          outputFormats={['srt']}
          onMethodChange={handleChange}
          onFormatChange={vi.fn()}
          onAsrConfigChange={vi.fn()}
          showVadConfig={false}
          showAsrAdvancedConfig={false}
        />
      </TestWrapper>
    )

    // Get the language select element
    const languageSelect = screen.getByLabelText(/language:/i) as HTMLSelectElement
    const options = Array.from(languageSelect.querySelectorAll('option'))

    // Find the Japanese option
    const japaneseOption = options.find(opt => opt.value === 'ja')

    // Japanese option should exist and have correct label
    expect(japaneseOption).toBeDefined()
    expect(japaneseOption?.textContent).toBe('Japanese')
  })
})
