// src/utils/errorHandler.spec.ts
import { describe, it, expect, vi } from 'vitest';
import {
  parseApiError,
  handleFileUploadError,
  handleASRError,
  handleScanError,
  logError,
  createError
} from './errorHandler';
import type { AxiosError } from '../types';

describe('parseApiError', () => {
  it('should return message for unknown error', () => {
    expect(parseApiError(null)).toBe('An unknown error occurred');
    expect(parseApiError(undefined)).toBe('An unknown error occurred');
  });

  it('should extract detail from axios response', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Invalid input' }
      }
    };
    expect(parseApiError(error)).toBe('Invalid input');
  });

  it('should extract message from axios response', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { message: 'Something went wrong' }
      }
    };
    expect(parseApiError(error)).toBe('Something went wrong');
  });

  it('should return HTTP status based messages', () => {
    const badRequestError: AxiosError = { response: { status: 400, data: {} } };
    expect(parseApiError(badRequestError)).toBe('Invalid request. Please check your input.');

    const unauthorizedError: AxiosError = { response: { status: 401, data: {} } };
    expect(parseApiError(unauthorizedError)).toBe('Authentication required. Please check your API credentials.');

    const forbiddenError: AxiosError = { response: { status: 403, data: {} } };
    expect(parseApiError(forbiddenError)).toBe('Access denied. You do not have permission to perform this action.');

    const notFoundError: AxiosError = { response: { status: 404, data: {} } };
    expect(parseApiError(notFoundError)).toBe('Resource not found. Please check the URL or file path.');

    const serverError: AxiosError = { response: { status: 500, data: {} } };
    expect(parseApiError(serverError)).toBe('Server error. Please try again later.');
  });

  it('should return status code for unknown status', () => {
    const error: AxiosError = { response: { status: 418, data: {} } };
    expect(parseApiError(error)).toBe('Request failed with status 418');
  });

  it('should extract message from error object', () => {
    const error = { message: 'Custom error message' };
    expect(parseApiError(error)).toBe('Custom error message');
  });

  it('should return fallback for error without message', () => {
    const error = {};
    expect(parseApiError(error)).toBe('An error occurred while processing your request');
  });
});

describe('handleFileUploadError', () => {
  it('should handle file too large error', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'File too large' }
      }
    };
    expect(handleFileUploadError(error)).toBe('File size exceeds the maximum limit');
  });

  it('should handle invalid file type error', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Invalid file type' }
      }
    };
    expect(handleFileUploadError(error)).toBe('Invalid file type. Please upload audio or video files');
  });

  it('should handle network errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Network connection failed' }
      }
    };
    expect(handleFileUploadError(error)).toBe('Network error. Please check your internet connection');
  });

  it('should pass through other errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Some other error' }
      }
    };
    expect(handleFileUploadError(error)).toBe('Some other error');
  });
});

describe('handleASRError', () => {
  it('should handle plugin errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'plugin not found' }
      }
    };
    expect(handleASRError(error)).toBe('ASR plugin error. Please check your ASR configuration');
  });

  it('should handle file processing errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'media file is corrupted' }
      }
    };
    expect(handleASRError(error)).toBe('Failed to process media file. Please ensure the file is valid');
  });

  it('should handle timeout errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Processing timeout' }
      }
    };
    expect(handleASRError(error)).toBe('Processing timeout. The file may be too large or processing took too long');
  });

  it('should handle authentication errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Invalid API key' }
      }
    };
    expect(handleASRError(error)).toBe('Authentication error. Please check your API credentials');
  });

  it('should pass through other errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Some other error' }
      }
    };
    expect(handleASRError(error)).toBe('Some other error');
  });
});

describe('handleScanError', () => {
  it('should handle path errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Invalid path' }
      }
    };
    expect(handleScanError(error)).toBe('Invalid path. Please check the directory path and permissions');
  });

  it('should handle permission errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'access permission error' }
      }
    };
    expect(handleScanError(error)).toBe('Permission denied. Please check file system permissions');
  });

  it('should handle not found errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Directory not found' }
      }
    };
    expect(handleScanError(error)).toBe('Directory not found. Please verify the path');
  });

  it('should pass through other errors', () => {
    const error: AxiosError = {
      response: {
        status: 400,
        data: { detail: 'Some other error' }
      }
    };
    expect(handleScanError(error)).toBe('Some other error');
  });
});

describe('logError', () => {
  it('should log error with context', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Test error');
    logError(error, 'TestContext');
    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });

  it('should log error with default context', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Test error');
    logError(error);
    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });

  it('should log stack trace if available', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Test error');
    logError(error, 'TestContext');
    expect(consoleSpy).toHaveBeenCalledTimes(2); // Error and stack
    consoleSpy.mockRestore();
  });
});

describe('createError', () => {
  it('should create error with message', () => {
    const error = createError('Test error');
    expect(error).toBeInstanceOf(Error);
    expect(error.message).toBe('Test error');
  });

  it('should attach context to error', () => {
    const context = { userId: 123, action: 'upload' };
    const error = createError('Test error', context);
    expect((error as Error & { context: typeof context }).context).toEqual(context);
  });

  it('should create error with empty context by default', () => {
    const error = createError('Test error');
    expect((error as Error & { context: Record<string, unknown> }).context).toEqual({});
  });
});
