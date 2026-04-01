// Application constants and configuration
import type { OutputFormat, LanguageCode, ASRMethodConfig } from '../types';

export const API_BASE_URL = 'http://localhost:8000/api/v1';

// Available output formats
export const OUTPUT_FORMATS: OutputFormat[] = ['srt', 'vtt', 'txt', 'ass', 'lrc'];

// Default output formats
export const DEFAULT_OUTPUT_FORMATS: OutputFormat[] = ['srt'];

// VAD configuration defaults
export const DEFAULT_MIN_SPEECH_DURATION = 500;
export const DEFAULT_MIN_SILENCE_DURATION = 500;

// Language option
export interface LanguageOption {
  value: LanguageCode;
  label: string;
}

// Language options
export const LANGUAGE_OPTIONS: LanguageOption[] = [
  { value: 'auto', label: 'Auto Detect' },
  { value: 'zh', label: 'Chinese' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: 'Japanese' }
];

// File upload limits
export const MAX_FILES = 10;


// ASR method specific configurations
export const ASR_METHOD_CONFIGS: Record<string, ASRMethodConfig> = {
  'whisper-api': {
    apiUrl: {
      placeholder: 'https://asr-ai.${LAZYCAT_BOX_DOMAIN}/v1/audio/transcriptions',
      description: 'ASR API URL'
    },
    apiKey: {
      placeholder: 'API Key',
      description: 'ASR API Key'
    },
    model: {
      placeholder: 'fun-asr-nano',
      description: 'Model name (fun-asr-nano / sensevoice-small / paraformer-large)'
    }
  }
};
