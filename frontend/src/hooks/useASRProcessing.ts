import { useState, useCallback, useEffect, useRef } from 'react';
import { processSingleFile, processMultipleFiles } from '../services/api';
import {
  DEFAULT_MIN_SPEECH_DURATION,
  DEFAULT_MIN_SILENCE_DURATION
} from '../constants/config';
import type { ProcessResult, LanguageCode, OutputFormat } from '../types';
import { useWebSocket } from './useWebSocket';
import type { WSMessage, WSStatusData } from '../types';

/** Form data options for ASR processing */
export interface ASRProcessingOptions {
  audioFiles: File[];
  asrMethod: string;
  outputFormats: OutputFormat[];
  showAdvancedOptions: boolean;
  minSpeechDuration: number;
  minSilenceDuration: number;
  asrApiUrl: string;
  asrApiKey: string;
  asrModel: string;
  asrLanguage: LanguageCode;
  outputMode?: 'task' | 'inline';
  isMultiple?: boolean;
}

/** Extended return type for useASRProcessing hook with WebSocket support */
export interface UseASRProcessingReturn {
  isProcessing: boolean;
  error: string | null;
  result: ProcessResult[] | null;
  multiFileResult: ProcessResult[] | null;
  resetResults: () => void;
  handleSingleSubmit: (formData: FormData) => Promise<void>;
  handleMultipleSubmit: (formData: FormData) => Promise<void>;
  buildFormData: (options: ASRProcessingOptions) => FormData;
  // WebSocket progress state
  progress: number;
  currentStage: string;
  progressMessage: string;
  connected: boolean;
}

/** Processing stage types */
type ProcessingStage =
  | 'idle'
  | 'preparing'
  | 'vad_segmentation'
  | 'loading_plugin'
  | 'exporting_segments'
  | 'transcription'
  | 'generating_subtitles'
  | 'completed'
  | 'error';

/**
 * Custom hook for ASR processing logic with WebSocket real-time updates
 */
export function useASRProcessing(): UseASRProcessingReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessResult[] | null>(null);
  const [multiFileResult, setMultiFileResult] = useState<ProcessResult[] | null>(null);

  // WebSocket progress state
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState<ProcessingStage>('idle');
  const [progressMessage, setProgressMessage] = useState('');

  // Track the current task ID for WebSocket subscription
  const taskIdRef = useRef<string | null>(null);

  // Setup WebSocket connection for task updates
  const { connected, lastStatus } = useWebSocket(taskIdRef.current);

  // Handle WebSocket status updates
  useEffect(() => {
    if (lastStatus && lastStatus.task_id === taskIdRef.current) {
      // Update progress from WebSocket
      if (typeof lastStatus.progress === 'number') {
        setProgress(lastStatus.progress);
      }
      if (lastStatus.status) {
        setCurrentStage(lastStatus.status as ProcessingStage);
      }
      if (lastStatus.message) {
        setProgressMessage(lastStatus.message);
      }

      // Check for completion
      if (lastStatus.status === 'completed' || lastStatus.status === 'error') {
        setIsProcessing(false);
      }
    }
  }, [lastStatus]);

  const resetResults = useCallback(() => {
    setError(null);
    setResult(null);
    setMultiFileResult(null);
    setProgress(0);
    setCurrentStage('idle');
    setProgressMessage('');
    taskIdRef.current = null;
  }, []);

  const handleSingleSubmit = useCallback(async (formData: FormData) => {
    setIsProcessing(true);
    resetResults();
    setProgress(10);
    setCurrentStage('preparing');
    setProgressMessage('Starting ASR processing...');

    try {
      const response = await processSingleFile(formData);

      // Extract task_id from response for WebSocket subscription
      if (response && response.length > 0 && response[0].taskId) {
        taskIdRef.current = response[0].taskId;
      }

      setResult(response);
      setProgress(100);
      setCurrentStage('completed');
      setProgressMessage('Processing completed successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setCurrentStage('error');
      setProgressMessage(err instanceof Error ? err.message : 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  }, [resetResults]);

  const handleMultipleSubmit = useCallback(async (formData: FormData) => {
    setIsProcessing(true);
    resetResults();
    setProgress(10);
    setCurrentStage('preparing');
    setProgressMessage('Starting batch processing...');

    try {
      const response = await processMultipleFiles(formData);

      // Extract task_id from first result for WebSocket subscription
      if (response && response.length > 0 && response[0].taskId) {
        taskIdRef.current = response[0].taskId;
      }

      setMultiFileResult(response);
      setProgress(100);
      setCurrentStage('completed');
      setProgressMessage('Batch processing completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setCurrentStage('error');
      setProgressMessage(err instanceof Error ? err.message : 'Batch processing failed');
    } finally {
      setIsProcessing(false);
    }
  }, [resetResults]);

  const buildFormData = useCallback(({
    audioFiles,
    asrMethod,
    outputFormats,
    showAdvancedOptions,
    minSpeechDuration,
    minSilenceDuration,
    asrApiUrl,
    asrApiKey,
    asrModel,
    asrLanguage,
    outputMode = 'task',  // Default to task directory output
    isMultiple = false
  }: ASRProcessingOptions): FormData => {
    const formData = new FormData();

    if (isMultiple) {
      // Add all files for multiple processing
      audioFiles.forEach(file => {
        formData.append('audio_files', file);
      });
    } else {
      // Add single file for single processing
      formData.append('media_file', audioFiles[0]);
    }

    formData.append('asr_method', asrMethod);
    formData.append('output_formats', outputFormats.join(','));
    formData.append('output_mode', outputMode);  // Add output mode parameter

    // Add VAD parameters
    if (showAdvancedOptions) {
      formData.append('min_speech_duration', (minSpeechDuration || DEFAULT_MIN_SPEECH_DURATION).toString());
      formData.append('min_silence_duration', (minSilenceDuration || DEFAULT_MIN_SILENCE_DURATION).toString());

      // Add ASR configuration parameters
      if (asrApiUrl) formData.append('asr_api_url', asrApiUrl);
      if (asrApiKey) formData.append('asr_api_key', asrApiKey);
      if (asrModel) formData.append('asr_model', asrModel);
      // Add language parameter
      formData.append('language', asrLanguage || 'auto');
    }

    return formData;
  }, []);

  return {
    isProcessing,
    error,
    result,
    multiFileResult,
    resetResults,
    handleSingleSubmit,
    handleMultipleSubmit,
    buildFormData,
    progress,
    currentStage,
    progressMessage,
    connected,
  };
}

export default useASRProcessing;
