// src/types/index.ts

/** Supported output formats for subtitle/text generation */
export type OutputFormat = 'srt' | 'vtt' | 'txt' | 'json' | 'ass' | 'lrc';

/** Supported language codes */
export type LanguageCode = 'auto' | 'zh' | 'en' | 'ja' | 'ko' | 'yue';

/** Processing status for tasks */
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

/** Scan status */
export type ScanStatus = 'idle' | 'scanning' | 'completed' | 'failed' | 'cancelled';

/** Monitor status */
export type MonitorStatus = 'active' | 'inactive' | 'error';

/** ASR plugin information */
export interface ASRPlugin {
  name: string;
  display_name: string;
  description?: string;
  supported_languages: LanguageCode[];
  requires_api_key: boolean;
  requires_api_url: boolean;
  model_parameter?: string;
}

/** ASR configuration */
export interface ASRConfig {
  method: string;
  language: LanguageCode;
  apiUrl: string;
  apiKey: string;
  model: string;
}

/** VAD (Voice Activity Detection) configuration */
export interface VADConfig {
  outputFormats: OutputFormat[];
  minSpeechDuration: number;
  minSilenceDuration: number;
}

/** Path scanner configuration */
export interface ScannerConfig {
  maxFiles: number;
  recursive: boolean;
}

/** File processing result */
export interface ProcessResult {
  success: boolean;
  filePath: string;
  outputFiles: string[];
  duration?: number;
  error?: string;
  taskId?: string;
}

/** Scan request payload */
export interface ScanRequest {
  path: string;
  max_files?: number;
  recursive?: boolean;
  file_patterns?: string[];
  asr_method?: string;
  output_formats?: string[];
}

/** Scan result response */
export interface ScanResult {
  scan_id: string;
  status: ScanStatus;
  total_files: number;
  processed_files: number;
  failed_files: number;
  results: ProcessResult[];
  error?: string;
}

/** Scan status response */
export interface ScanStatusResponse {
  scan_id: string;
  status: ScanStatus;
  progress: number;
  total_files: number;
  processed_files: number;
  current_file?: string;
  error?: string;
}

/** Directory browse result */
export interface DirectoryBrowseResult {
  path: string;
  subdirectories: string[];
  media_files: MediaFileInfo[];
}

/** Media file information */
export interface MediaFileInfo {
  name: string;
  path: string;
  size: number;
  modified_time: string;
}

/** Path information */
export interface PathInfo {
  path: string;
  exists: boolean;
  is_directory: boolean;
  is_readable: boolean;
  size?: number;
  error?: string;
}

/** Monitor configuration */
export interface MonitorConfig {
  monitor_id?: string;
  name: string;
  watch_path: string;
  recursive: boolean;
  file_patterns: string[];
  asr_method: string;
  language: LanguageCode;
  output_formats: OutputFormat[];
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

/** Monitor list response */
export interface MonitorListResponse {
  monitors: MonitorConfig[];
  total_count: number;
  active_count: number;
}

/** Monitor service status */
export interface MonitorServiceStatus {
  is_running: boolean;
  active_monitors: number;
  total_monitors: number;
  uptime_seconds?: number;
}

/** Database status */
export interface DatabaseStatus {
  is_connected: boolean;
  database_type: string;
  database_path?: string;
  total_records?: number;
  last_checked: string;
}

/** API error response structure */
export interface ApiErrorResponse {
  detail?: string;
  message?: string;
  code?: string;
}

/** Axios-like error structure */
export interface AxiosError {
  response?: {
    status: number;
    data: ApiErrorResponse;
  };
  message?: string;
  stack?: string;
}

/** Global configuration state */
export interface ConfigState {
  // ASR Configuration
  asrMethod: string;
  availablePlugins: ASRPlugin[];
  asrLanguage: LanguageCode;
  asrApiUrl: string;
  asrApiKey: string;
  asrModel: string;

  // VAD Configuration
  outputFormats: OutputFormat[];
  minSpeechDuration: number;
  minSilenceDuration: number;

  // Path Scanner specific
  maxFiles: number;
  recursive: boolean;

  // UI State
  isProcessing: boolean;
}

/** Config context actions */
export interface ConfigActions {
  setAsrMethod: (method: string) => void;
  setAvailablePlugins: (plugins: ASRPlugin[]) => void;
  setAsrLanguage: (language: LanguageCode) => void;
  setAsrApiUrl: (url: string) => void;
  setAsrApiKey: (key: string) => void;
  setAsrModel: (model: string) => void;
  toggleOutputFormat: (format: OutputFormat) => void;
  setMinSpeechDuration: (duration: number) => void;
  setMinSilenceDuration: (duration: number) => void;
  setMaxFiles: (max: number) => void;
  setRecursive: (recursive: boolean) => void;
  setProcessing: (isProcessing: boolean) => void;
  resetConfig: () => void;
}

/** Config context value */
export interface ConfigContextValue {
  state: ConfigState;
  actions: ConfigActions;
}

/** Tab type for navigation */
export type TabType = 'upload' | 'scanner' | 'monitor';

/** ASR method field configuration */
export interface ASRFieldConfig {
  placeholder?: string;
  value?: string;
  readOnly?: boolean;
  description: string;
  options?: Array<{ value: string; label: string }>;
}

/** ASR method configuration */
export interface ASRMethodConfig {
  apiUrl?: ASRFieldConfig;
  apiKey?: ASRFieldConfig;
  model?: ASRFieldConfig;
}

// Re-export all WebSocket types from websocket.ts
// This includes WSMessage, WSMessageType, WSMessageData, etc.
export type {
  WSMessage,
  WSMessageType,
  WSMessageData,
  WSConnectionStatus,
  ASRProgressData,
  ASRProcessingStage,
  ScanProgressData,
  TaskProgressData,
  TaskStatus,
  ErrorMessageData,
  PingMessageData,
  ASRProcessingStats,
  FailedSegmentDetail,
  WSConnectionState,
} from './websocket';
