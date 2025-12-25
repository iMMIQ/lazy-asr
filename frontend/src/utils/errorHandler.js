/**
 * Error Handler utility functions
 * Provides centralized error handling for the application
 */

/**
 * Parse API error response
 * @param {Error|Object} error - Error object or response
 * @returns {string} User-friendly error message
 */
export function parseApiError(error) {
    if (!error) {
        return 'An unknown error occurred';
    }

    // If error has response property (axios-like)
    if (error.response) {
        const { status, data } = error.response;

        // Server returned error with details
        if (data && data.detail) {
            return data.detail;
        }

        if (data && data.message) {
            return data.message;
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
    if (error.message) {
        return error.message;
    }

    // Fallback
    return 'An error occurred while processing your request';
}

/**
 * Handle file upload error
 * @param {Error} error - Error object
 * @returns {string} User-friendly error message
 */
export function handleFileUploadError(error) {
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
 * @param {Error} error - Error object
 * @returns {string} User-friendly error message
 */
export function handleASRError(error) {
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
 * @param {Error} error - Error object
 * @returns {string} User-friendly error message
 */
export function handleScanError(error) {
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
 * @param {Error} error - Error object
 * @param {string} context - Context where error occurred
 */
export function logError(error, context = 'Application') {
    console.error(`[${context}] Error:`, error);

    if (error.stack) {
        console.error(`[${context}] Stack:`, error.stack);
    }
}

/**
 * Create error object with additional context
 * @param {string} message - Error message
 * @param {Object} context - Additional context
 * @returns {Error} Enhanced error object
 */
export function createError(message, context = {}) {
    const error = new Error(message);
    error.context = context;
    return error;
}
