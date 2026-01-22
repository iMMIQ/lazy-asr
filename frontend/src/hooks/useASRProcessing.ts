import { useState, useCallback } from 'react';
import { processSingleFile, processMultipleFiles } from '../services/api';
import {
  DEFAULT_MIN_SPEECH_DURATION,
  DEFAULT_MIN_SILENCE_DURATION
} from '../constants/config';
import type { ProcessResult, LanguageCode, OutputFormat } from '../types';

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

/** Return type for useASRProcessing hook */
export interface UseASRProcessingReturn {
  isProcessing: boolean;
  error: string | null;
  result: ProcessResult[] | null;
  multiFileResult: ProcessResult[] | null;
  resetResults: () => void;
  handleSingleSubmit: (formData: FormData) => Promise<void>;
  handleMultipleSubmit: (formData: FormData) => Promise<void>;
  buildFormData: (options: ASRProcessingOptions) => FormData;
}

/**
 * Custom hook for ASR processing logic
 */
export function useASRProcessing(): UseASRProcessingReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessResult[] | null>(null);
  const [multiFileResult, setMultiFileResult] = useState<ProcessResult[] | null>(null);

  const resetResults = useCallback(() => {
    setError(null);
    setResult(null);
    setMultiFileResult(null);
  }, []);

  const handleSingleSubmit = useCallback(async (formData: FormData) => {
    setIsProcessing(true);
    resetResults();

    try {
      const response = await processSingleFile(formData);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsProcessing(false);
    }
  }, [resetResults]);

  const handleMultipleSubmit = useCallback(async (formData: FormData) => {
    setIsProcessing(true);
    resetResults();

    try {
      const response = await processMultipleFiles(formData);
      setMultiFileResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
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
    buildFormData
  };
}

export default useASRProcessing;
