/**
 * Tests for useASRProcessing hook with WebSocket integration
 */
import { renderHook, waitFor, act } from '@testing-library/react';
import { vi, beforeEach, afterEach, describe, it, expect } from 'vitest';
import { useASRProcessing } from './useASRProcessing';

// Mock the WebSocket connection
vi.mock('./useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    connected: true,
    lastMessage: null,
    lastStatus: null,
    status: 'connected' as const,
    sendMessage: vi.fn(),
    disconnect: vi.fn(),
    reconnect: vi.fn(),
  })),
}));

// Mock the API service
vi.mock('../services/api', () => ({
  processSingleFile: vi.fn(() => Promise.resolve([
    {
      success: true,
      filePath: '/path/to/audio.wav',
      outputFiles: ['/path/to/output.srt'],
      taskId: 'test-task-123',
    },
  ])),
  processMultipleFiles: vi.fn(() => Promise.resolve([
    {
      success: true,
      filePath: '/path/to/audio1.wav',
      outputFiles: ['/path/to/audio1.srt'],
      taskId: 'test-task-456',
    },
  ])),
}));

describe('useASRProcessing with WebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useASRProcessing());

    expect(result.current.isProcessing).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.result).toBe(null);
    expect(result.current.multiFileResult).toBe(null);
  });

  it('should handle single file submission', async () => {
    const { result } = renderHook(() => useASRProcessing());

    const formData = new FormData();
    formData.append('media_file', new File(['audio'], 'test.wav', { type: 'audio/wav' }));
    formData.append('asr_method', 'whisper-api');

    await act(async () => {
      await result.current.handleSingleSubmit(formData);
    });

    await waitFor(() => {
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.result).not.toBe(null);
    });
  });

  it('should handle multiple files submission', async () => {
    const { result } = renderHook(() => useASRProcessing());

    const formData = new FormData();
    formData.append('audio_files', new File(['audio1'], 'test1.wav', { type: 'audio/wav' }));
    formData.append('audio_files', new File(['audio2'], 'test2.wav', { type: 'audio/wav' }));
    formData.append('asr_method', 'whisper-api');

    await act(async () => {
      await result.current.handleMultipleSubmit(formData);
    });

    await waitFor(() => {
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.multiFileResult).not.toBe(null);
    });
  });

  it('should build FormData correctly', () => {
    const { result } = renderHook(() => useASRProcessing());

    const options = {
      audioFiles: [new File(['audio'], 'test.wav', { type: 'audio/wav' })] as File[],
      asrMethod: 'whisper-api',
      outputFormats: ['srt', 'vtt'] as const,
      showAdvancedOptions: true,
      minSpeechDuration: 250,
      minSilenceDuration: 100,
      asrApiUrl: 'http://example.com/api',
      asrApiKey: 'test-key',
      asrModel: 'large',
      asrLanguage: 'en' as const,
      outputMode: 'task' as const,
      isMultiple: false,
    };

    const formData = result.current.buildFormData(options);

    expect(formData.get('media_file')).toBeInstanceOf(File);
    expect(formData.get('asr_method')).toBe('whisper-api');
    expect(formData.get('output_formats')).toBe('srt,vtt');
    expect(formData.get('output_mode')).toBe('task');
    expect(formData.get('min_speech_duration')).toBe('250');
    expect(formData.get('min_silence_duration')).toBe('100');
    expect(formData.get('asr_api_url')).toBe('http://example.com/api');
    expect(formData.get('asr_api_key')).toBe('test-key');
    expect(formData.get('asr_model')).toBe('large');
    expect(formData.get('language')).toBe('en');
  });

  it('should build FormData for multiple files', () => {
    const { result } = renderHook(() => useASRProcessing());

    const options = {
      audioFiles: [
        new File(['audio1'], 'test1.wav', { type: 'audio/wav' }),
        new File(['audio2'], 'test2.wav', { type: 'audio/wav' }),
      ] as File[],
      asrMethod: 'faster-whisper',
      outputFormats: ['txt'] as const,
      showAdvancedOptions: false,
      minSpeechDuration: 250,
      minSilenceDuration: 100,
      asrApiUrl: '',
      asrApiKey: '',
      asrModel: '',
      asrLanguage: 'auto' as const,
      isMultiple: true,
    };

    const formData = result.current.buildFormData(options);

    expect(formData.get('asr_method')).toBe('faster-whisper');
    expect(formData.get('output_formats')).toBe('txt');

    // Check that multiple files are added
    const audioFiles = formData.getAll('audio_files');
    expect(audioFiles).toHaveLength(2);
  });

  it('should reset results when resetResults is called', () => {
    const { result } = renderHook(() => useASRProcessing());

    // Set some results (simulate processing completed)
    // Note: In real scenario, this would happen after handleSingleSubmit

    act(() => {
      result.current.resetResults();
    });

    expect(result.current.error).toBe(null);
    expect(result.current.result).toBe(null);
    expect(result.current.multiFileResult).toBe(null);
  });

  it('should handle errors during processing', async () => {
    const { processSingleFile } = await import('../services/api');

    // Mock an error response
    vi.mocked(processSingleFile).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useASRProcessing());

    const formData = new FormData();
    formData.append('media_file', new File(['audio'], 'test.wav', { type: 'audio/wav' }));
    formData.append('asr_method', 'whisper-api');

    await act(async () => {
      await result.current.handleSingleSubmit(formData);
    });

    await waitFor(() => {
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.error).not.toBe(null);
      expect(result.current.error).toBe('Network error');
    });
  });

  it('should track processing state correctly', async () => {
    const { result } = renderHook(() => useASRProcessing());

    expect(result.current.isProcessing).toBe(false);

    const formData = new FormData();
    formData.append('media_file', new File(['audio'], 'test.wav', { type: 'audio/wav' }));
    formData.append('asr_method', 'whisper-api');

    // Start processing
    const processingPromise = act(async () => {
      await result.current.handleSingleSubmit(formData);
    });

    // During processing, isProcessing should be true
    // Note: This depends on timing and might need adjustment

    await processingPromise;

    // After processing, isProcessing should be false
    await waitFor(() => {
      expect(result.current.isProcessing).toBe(false);
    });
  });
});
