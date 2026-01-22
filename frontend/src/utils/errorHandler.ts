/**
 * Error Handler utility functions
 * Provides centralized error handling for the application
 */
import type { AxiosError, ApiErrorResponse } from '../types';

/**
 * Parse API error response
 * @param error - Error object or response
 * @returns User-friendly error message
 */
export function parseApiError(error: AxiosError | Partial<Error> | null | undefined): string {
  if (!error) {
    return 'An unknown error occurred';
  }

  // If error has response property (axios-like)
  if ('response' in error && error.response) {
    const { status, data } = error.response;

    // Server returned error with details
    if (data && typeof data === 'object' && 'detail' in data) {
      return String((data as ApiErrorResponse).detail);
    }

    if (data && typeof data === 'object' && 'message' in data) {
      return String((data as ApiErrorResponse).message);
    }

    // HTTP status based messages
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please check your API credentials.';
      case 403:
        return 'Access denied. You do not have permission to perform this action.';
      case 404:
        return 'Resource not found. Please check the URL or file path.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return `Request failed with status ${status}`;
    }
  }

  // If error has message property
  if ('message' in error && typeof error.message === 'string') {
    return error.message;
  }

  // Fallback
  return 'An error occurred while processing your request';
}

/**
 * Handle file upload error
 * @param error - Error object
 * @returns User-friendly error message
 */
export function handleFileUploadError(error: AxiosError | Error): string {
  const message = parseApiError(error);

  if (message.includes('File too large')) {
    return 'File size exceeds the maximum limit';
  }

  if (message.includes('Invalid file type')) {
    return 'Invalid file type. Please upload audio or video files';
  }

  if (message.includes('network') || message.includes('connection')) {
    return 'Network error. Please check your internet connection';
  }

  return message;
}

/**
 * Handle ASR processing error
 * @param error - Error object
 * @returns User-friendly error message
 */
export function handleASRError(error: AxiosError | Error): string {
  const message = parseApiError(error);

  if (message.includes('plugin') || message.includes('ASR method')) {
    return 'ASR plugin error. Please check your ASR configuration';
  }

  if (message.includes('file') || message.includes('media')) {
    return 'Failed to process media file. Please ensure the file is valid';
  }

  if (message.includes('timeout')) {
    return 'Processing timeout. The file may be too large or processing took too long';
  }

  if (message.includes('API key') || message.includes('authentication')) {
    return 'Authentication error. Please check your API credentials';
  }

  return message;
}

/**
 * Handle scan error
 * @param error - Error object
 * @returns User-friendly error message
 */
export function handleScanError(error: AxiosError | Error): string {
  const message = parseApiError(error);

  if (message.includes('path') || message.includes('directory')) {
    return 'Invalid path. Please check the directory path and permissions';
  }

  if (message.includes('permission') || message.includes('access')) {
    return 'Permission denied. Please check file system permissions';
  }

  if (message.includes('not found')) {
    return 'Directory not found. Please verify the path';
  }

  return message;
}

/**
 * Log error to console with context
 * @param error - Error object
 * @param context - Context where error occurred
 */
export function logError(error: Error, context: string = 'Application'): void {
  console.error(`[${context}] Error:`, error);

  if (error.stack) {
    console.error(`[${context}] Stack:`, error.stack);
  }
}

/**
 * Create error object with additional context
 * @param message - Error message
 * @param context - Additional context
 * @returns Enhanced error object
 */
export function createError(message: string, context: Record<string, unknown> = {}): Error & { context: Record<string, unknown> } {
  const error = new Error(message) as Error & { context: Record<string, unknown> };
  error.context = context;
  return error;
}
