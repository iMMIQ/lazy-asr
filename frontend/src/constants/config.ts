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
  'faster-whisper': {
    apiUrl: {
      placeholder: 'https://funasr-ai.immiqtop.heiyu.space/v1/audio/transcriptions',
      description: 'Faster Whisper API URL'
    },
    apiKey: {
      placeholder: 'API Key',
      description: 'Faster Whisper API Key'
    },
    model: {
      placeholder: 'fun-asr-nano',
      description: 'Model name for Faster Whisper'
    }
  },
  'qwen-asr': {
    apiUrl: {
      value: 'https://dashscope.aliyuncs.com/api/v1/services/aigc/audio/asr',
      readOnly: true,
      description: 'Qwen ASR API URL'
    },
    apiKey: {
      placeholder: 'Enter Alibaba Cloud API Key',
      description: 'Alibaba Cloud API Key'
    },
    model: {
      options: [
        { value: 'qwen3-asr-flash', label: 'qwen3-asr-flash' }
      ],
      description: 'Model for Qwen ASR'
    }
  }
};
