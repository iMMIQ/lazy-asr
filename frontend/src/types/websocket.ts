/**
 * TypeScript type definitions for WebSocket messages
 *
 * This file contains all type definitions related to WebSocket communication
 * between the frontend and backend for real-time updates.
 */

/** Base WebSocket message types */
export type WSMessageType = 'status' | 'error' | 'ping' | 'pong' | 'progress';

/** Processing stage for ASR tasks */
export type ASRProcessingStage =
  | 'idle'
  | 'preparing'
  | 'vad_segmentation'
  | 'loading_plugin'
  | 'exporting_segments'
  | 'transcription'
  | 'generating_subtitles'
  | 'completed'
  | 'error';

/** Scan status for path scanning operations */
export type ScanStatus = 'idle' | 'scanning' | 'completed' | 'failed' | 'cancelled';

/** Task status for ASR processing */
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

/**
 * Base WebSocket message interface
 */
export interface WSMessage<T = WSMessageData> {
  type: WSMessageType;
  data?: T;
  message?: string;
  timestamp?: string;
}

/**
 * Union type for all WebSocket message data types
 */
export type WSMessageData =
  | ASRProgressData
  | ScanProgressData
  | TaskProgressData
  | ErrorMessageData
  | PingMessageData;

/**
 * ASR processing progress data
 * Sent during ASR file processing to report progress
 */
export interface ASRProgressData {
  task_id: string;
  stage: ASRProcessingStage;
  progress: number; // 0-100
  message: string;
  /** Additional context data */
  media_path?: string;
  current_segment?: number;
  total_segments?: number;
  stats?: ASRProcessingStats;
  output_files?: string[];
  error?: string;
}

/**
 * Scan progress data
 * Sent during path scanning operations
 */
export interface ScanProgressData {
  scan_id: string;
  status: ScanStatus;
  progress: number; // 0-100
  total_files: number;
  processed_files: number;
  failed_files: number;
  current_file?: string;
  error?: string;
}

/**
 * Generic task progress data
 * Used for general task status updates
 */
export interface TaskProgressData {
  task_id: string;
  status: TaskStatus;
  progress: number; // 0-100
  message: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Error message data
 * Sent when an error occurs during processing
 */
export interface ErrorMessageData {
  task_id?: string;
  scan_id?: string;
  error: string;
  error_type?: string;
  context?: Record<string, unknown>;
}

/**
 * Ping/pong message data for heartbeat
 */
export interface PingMessageData {
  timestamp?: string;
}

/**
 * ASR processing statistics
 */
export interface ASRProcessingStats {
  total_segments: number;
  successful_transcriptions: number;
  failed_segments: number;
  empty_segments: number;
  total_subtitles: number;
  output_formats: string[];
}

/**
 * Failed segment detail
 */
export interface FailedSegmentDetail {
  index: number;
  start_time: number;
  end_time: number;
  duration: number;
  file_path: string;
  error: string;
  error_type: string;
}

/**
 * WebSocket connection status
 */
export type WSConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * WebSocket connection state
 */
export interface WSConnectionState {
  status: WSConnectionStatus;
  connected: boolean;
  error: string | null;
  lastMessage: WSMessage | null;
  lastPingTime?: number;
}

/**
 * WebSocket configuration options
 */
export interface WSConnectionOptions {
  /** WebSocket server URL */
  baseUrl?: string;
  /** Enable automatic reconnection */
  autoReconnect?: boolean;
  /** Maximum number of reconnection attempts */
  maxReconnectAttempts?: number;
  /** Delay between reconnection attempts in ms */
  reconnectDelay?: number;
  /** Enable ping/pong heartbeat */
  enableHeartbeat?: boolean;
  /** Interval for sending ping messages in ms */
  heartbeatInterval?: number;
  /** Enable infinite reconnection attempts (default: false) */
  infiniteReconnect?: boolean;
}

/**
 * Message handler callback type
 */
export type WSMessageHandler<T = WSMessageData> = (message: WSMessage<T>) => void;

/**
 * Status change handler callback type
 */
export type WSStatusChangeHandler = (status: WSConnectionStatus) => void;

/**
 * Progress update handler callback type
 */
export type WSProgressHandler = (progress: number, stage: ASRProcessingStage) => void;

/**
 * WebSocket client interface
 * Defines the contract for WebSocket client implementations
 */
export interface IWebSocketClient {
  connect(): void;
  disconnect(): void;
  send(message: Record<string, unknown>): void;
  onMessage(handler: WSMessageHandler): void;
  onStatusChange(handler: WSStatusChangeHandler): void;
  getStatus(): WSConnectionStatus;
  isConnected(): boolean;
}

/**
 * Re-exports for backward compatibility
 * These were previously defined in types/index.ts
 */
export interface WSStatusData {
  scan_id: string;
  status: ScanStatus;
  progress: number;
  total_files: number;
  processed_files: number;
  current_file?: string;
  error?: string;
}

/**
 * Utility type for extracting message data by type
 */
export type GetMessageDataByType<T extends WSMessageType> = T extends 'status'
  ? ASRProgressData | ScanProgressData | TaskProgressData
  : T extends 'error'
  ? ErrorMessageData
  : T extends 'ping' | 'pong'
  ? PingMessageData
  : T extends 'progress'
  ? ASRProgressData
  : never;

/**
 * Type guard for checking if a message is ASR progress data
 */
export function isASRProgressData(data: unknown): data is ASRProgressData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'task_id' in data &&
    'stage' in data &&
    'progress' in data &&
    'message' in data
  );
}

/**
 * Type guard for checking if a message is scan progress data
 */
export function isScanProgressData(data: unknown): data is ScanProgressData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'scan_id' in data &&
    'status' in data &&
    'progress' in data
  );
}

/**
 * Type guard for checking if a message is error data
 */
export function isErrorMessageData(data: unknown): data is ErrorMessageData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data
  );
}

/**
 * Creates a typed WebSocket message
 */
export function createWSMessage<T extends WSMessageType>(
  type: T,
  data?: GetMessageDataByType<T>,
  message?: string
): WSMessage<GetMessageDataByType<T>> {
  return {
    type,
    data,
    message,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Parses a JSON string as a WebSocket message
 */
export function parseWSMessage(json: string): WSMessage | null {
  try {
    const parsed = JSON.parse(json);
    if (typeof parsed === 'object' && parsed !== null && 'type' in parsed) {
      return parsed as WSMessage;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Default export
 */
export default {
  ASRProcessingStage: {
    IDLE: 'idle' as const,
    PREPARING: 'preparing' as const,
    VAD_SEGMENTATION: 'vad_segmentation' as const,
    LOADING_PLUGIN: 'loading_plugin' as const,
    EXPORTING_SEGMENTS: 'exporting_segments' as const,
    TRANSCRIPTION: 'transcription' as const,
    GENERATING_SUBTITLES: 'generating_subtitles' as const,
    COMPLETED: 'completed' as const,
    ERROR: 'error' as const,
  },
  WSConnectionStatus: {
    CONNECTING: 'connecting' as const,
    CONNECTED: 'connected' as const,
    DISCONNECTED: 'disconnected' as const,
    ERROR: 'error' as const,
  },
  WSMessageType: {
    STATUS: 'status' as const,
    ERROR: 'error' as const,
    PING: 'ping' as const,
    PONG: 'pong' as const,
    PROGRESS: 'progress' as const,
  },
};
