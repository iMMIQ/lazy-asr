import { useState, useCallback } from 'react';
import { processSingleFile, processMultipleFiles } from '../services/api';
import { 
  DEFAULT_MIN_SPEECH_DURATION, 
  DEFAULT_MIN_SILENCE_DURATION,
  DEFAULT_OUTPUT_FORMATS 
} from '../constants/config';

/**
 * Custom hook for ASR processing logic
 */
export const useASRProcessing = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [multiFileResult, setMultiFileResult] = useState(null);

  const resetResults = useCallback(() => {
    setError(null);
    setResult(null);
    setMultiFileResult(null);
  }, []);

  const handleSingleSubmit = useCallback(async (formData) => {
    setIsProcessing(true);
    resetResults();

    try {
      const response = await processSingleFile(formData);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  }, [resetResults]);

  const handleMultipleSubmit = useCallback(async (formData) => {
    setIsProcessing(true);
    resetResults();

    try {
      const response = await processMultipleFiles(formData);
      setMultiFileResult(response);
    } catch (err) {
      setError(err.message);
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
    isMultiple = false
  }) => {
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

    // Add VAD parameters
    if (showAdvancedOptions) {
      formData.append('min_speech_duration', minSpeechDuration || DEFAULT_MIN_SPEECH_DURATION);
      formData.append('min_silence_duration', minSilenceDuration || DEFAULT_MIN_SILENCE_DURATION);

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
};

export default useASRProcessing;
