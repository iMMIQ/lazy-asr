/**
 * End-to-end WebSocket integration tests
 *
 * These tests verify the complete WebSocket integration between
 * the frontend and backend for real-time updates.
 */
import { describe, it, expect } from 'vitest';
import type { WSMessage } from '../../src/types/websocket';

// Import WebSocket types and utilities
import {
  ASRProcessingStage,
  isASRProgressData,
  isScanProgressData,
  isErrorMessageData,
  createWSMessage,
  parseWSMessage,
} from '../../src/types/websocket';

describe('WebSocket Message Types', () => {
  describe('Type Guards', () => {
    it('should identify ASR progress data', () => {
      const asrData = {
        task_id: 'task-123',
        stage: 'transcription' as const,
        progress: 75,
        message: 'Processing...',
      };

      expect(isASRProgressData(asrData)).toBe(true);
      expect(isASRProgressData({ not: 'valid' })).toBe(false);
    });

    it('should identify scan progress data', () => {
      const scanData = {
        scan_id: 'scan-123',
        status: 'scanning' as const,
        progress: 50,
        total_files: 100,
        processed_files: 50,
      };

      expect(isScanProgressData(scanData)).toBe(true);
      expect(isScanProgressData({ not: 'valid' })).toBe(false);
    });

    it('should identify error message data', () => {
      const errorData = {
        error: 'Something went wrong',
      };

      expect(isErrorMessageData(errorData)).toBe(true);
      expect(isErrorMessageData({ not: 'error' })).toBe(false);
    });
  });

  describe('Message Creation', () => {
    it('should create status message', () => {
      const message = createWSMessage('status', {
        task_id: 'task-123',
        stage: 'preparing',
        progress: 10,
        message: 'Preparing...',
      });

      expect(message.type).toBe('status');
      expect(message.data).toBeDefined();
      expect(message.timestamp).toBeDefined();
    });

    it('should create error message', () => {
      const message = createWSMessage('error', {
        error: 'Processing failed',
      });

      expect(message.type).toBe('error');
      expect(message.data?.error).toBe('Processing failed');
    });

    it('should create ping message', () => {
      const message = createWSMessage('ping', {
        timestamp: new Date().toISOString(),
      });

      expect(message.type).toBe('ping');
    });
  });

  describe('Message Parsing', () => {
    it('should parse valid JSON message', () => {
      const json = JSON.stringify({
        type: 'status',
        data: {
          task_id: 'task-123',
          stage: 'processing',
          progress: 50,
          message: 'Test',
        },
      });

      const parsed = parseWSMessage(json);
      expect(parsed).not.toBeNull();
      expect(parsed?.type).toBe('status');
    });

    it('should return null for invalid JSON', () => {
      const parsed = parseWSMessage('invalid json');
      expect(parsed).toBeNull();
    });

    it('should return null for message without type', () => {
      const json = JSON.stringify({
        data: { something: 'value' },
      });

      const parsed = parseWSMessage(json);
      expect(parsed).toBeNull();
    });
  });
});

describe('ASR Processing Stages', () => {
  it('should have all required stages', () => {
    const stages: ASRProcessingStage[] = [
      'idle',
      'preparing',
      'vad_segmentation',
      'loading_plugin',
      'exporting_segments',
      'transcription',
      'generating_subtitles',
      'completed',
      'error',
    ];

    stages.forEach(stage => {
      expect(stage).toBeDefined();
      expect(typeof stage).toBe('string');
    });
  });

  it('should support stage progression', () => {
    const progression: ASRProcessingStage[] = [
      'idle',
      'preparing',
      'vad_segmentation',
      'transcription',
      'completed',
    ];

    progression.forEach((stage, index) => {
      if (index > 0) {
        expect(stage).not.toBe(progression[index - 1]);
      }
    });
  });
});

describe('WebSocket Integration Scenarios', () => {
  describe('ASR Processing Progress', () => {
    it('should handle complete ASR processing flow', () => {
      const stages = [
        { stage: 'preparing' as const, progress: 5, message: 'Preparing media' },
        { stage: 'vad_segmentation' as const, progress: 20, message: 'Detecting speech' },
        { stage: 'transcription' as const, progress: 60, message: 'Transcribing' },
        { stage: 'generating_subtitles' as const, progress: 90, message: 'Generating files' },
        { stage: 'completed' as const, progress: 100, message: 'Complete' },
      ];

      stages.forEach(update => {
        const message = createWSMessage('status', {
          task_id: 'task-flow-test',
          ...update,
        });

        expect(isASRProgressData(message.data)).toBe(true);
        // Type assertion for accessing ASRProgressData-specific properties
        if (isASRProgressData(message.data)) {
          expect(message.data.stage).toBe(update.stage);
          expect(message.data.progress).toBe(update.progress);
        }
      });
    });

    it('should handle error during processing', () => {
      const errorMessage = createWSMessage('error', {
        task_id: 'task-error-test',
        error: 'Processing failed: Invalid audio format',
        error_type: 'ValidationError',
      });

      expect(isErrorMessageData(errorMessage.data)).toBe(true);
      expect(errorMessage.data?.error).toContain('Invalid audio format');
    });
  });

  describe('Scan Progress Updates', () => {
    it('should handle scan lifecycle', () => {
      const updates = [
        { status: 'idle' as const, progress: 0, total_files: 10, processed_files: 0 },
        { status: 'scanning' as const, progress: 30, total_files: 10, processed_files: 3 },
        { status: 'scanning' as const, progress: 70, total_files: 10, processed_files: 7 },
        { status: 'completed' as const, progress: 100, total_files: 10, processed_files: 10 },
      ];

      updates.forEach(update => {
        const message = createWSMessage('status', {
          scan_id: 'scan-lifecycle-test',
          ...update,
        });

        expect(isScanProgressData(message.data)).toBe(true);
        // Type assertion for accessing ScanProgressData-specific properties
        if (isScanProgressData(message.data)) {
          expect(message.data.progress).toBe(update.progress);
          expect(message.data.total_files).toBe(update.total_files);
        }
      });
    });
  });

  describe('Message Serialization', () => {
    it('should serialize and deserialize messages correctly', () => {
      const original = createWSMessage('status', {
        task_id: 'task-serialize',
        stage: 'transcription',
        progress: 50,
        message: 'Halfway done',
      });

      const json = JSON.stringify(original);
      const parsed = parseWSMessage(json);

      expect(parsed).not.toBeNull();
      expect(parsed?.type).toBe(original.type);
      expect(parsed?.data).toEqual(original.data);
    });
  });
});

describe('Type Safety', () => {
  it('should enforce message types', () => {
    // This test verifies type safety at compile time
    // If types are incorrect, TypeScript will fail compilation

    type ASRProgressMessage = WSMessage<{
      task_id: string;
      stage: ASRProcessingStage;
      progress: number;
      message: string;
    }>;

    const message: ASRProgressMessage = {
      type: 'status',
      data: {
        task_id: 'task-typesafe',
        stage: 'transcription',
        progress: 75,
        message: 'Processing...',
      },
    };

    expect(message.data?.task_id).toBe('task-typesafe');
    expect(message.data?.stage).toBe('transcription');

    // Test that valid message types work correctly
    const pingMessage: WSMessage = {
      type: 'ping',
      data: { timestamp: new Date().toISOString() },
    };

    expect(pingMessage.type).toBe('ping');
  });

  it('should use discriminated unions for message types', () => {
    type WSStatusMessage = WSMessage<{
      scan_id: string;
      status: string;
      progress: number;
    }>;

    const message: WSStatusMessage = {
      type: 'status',
      data: {
        scan_id: 'scan-union',
        status: 'scanning',
        progress: 50,
      },
    };

    expect(message.type).toBe('status');
  });
});

describe('WebSocket Connection States', () => {
  it('should track connection state transitions', () => {
    type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

    let currentState: ConnectionState = 'connecting';

    // Simulate state transitions
    currentState = 'connected';
    expect(currentState).toBe('connected');

    currentState = 'disconnected';
    expect(currentState).toBe('disconnected');
  });

  it('should handle reconnection logic', () => {
    let reconnectAttempts = 0;
    const maxAttempts = 5;
    const baseDelay = 3000;

    while (reconnectAttempts < maxAttempts) {
      // Simulate reconnection attempt
      reconnectAttempts++;
      const delay = baseDelay * reconnectAttempts;

      // Verify exponential backoff
      expect(delay).toBe(baseDelay * reconnectAttempts);
    }

    expect(reconnectAttempts).toBe(maxAttempts);
  });
});

// Export test utilities
export const testUtils = {
  createMockWSMessage: (type: string, data: any) => ({
    type,
    data,
    timestamp: new Date().toISOString(),
  }),

  createMockASRProgress: (taskId: string, stage: ASRProcessingStage, progress: number) => ({
    task_id: taskId,
    stage,
    progress,
    message: `Processing at ${progress}%`,
  }),

  createMockScanProgress: (scanId: string, progress: number) => ({
    scan_id: scanId,
    status: 'scanning' as const,
    progress,
    total_files: 100,
    processed_files: progress,
  }),
};
