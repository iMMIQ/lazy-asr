import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 600 seconds timeout
});

/**
 * Fetch available ASR plugins from backend
 */
export const fetchPlugins = async () => {
  try {
    const response = await apiClient.get('/asr/plugins');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch plugins:', error);
    throw new Error('Failed to fetch available ASR methods');
  }
};

/**
 * Process single audio file
 */
export const processSingleFile = async (formData) => {
  try {
    const response = await apiClient.post('/asr/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Single file processing failed:', error);
    throw new Error(error.response?.data?.detail || 'Processing failed');
  }
};

/**
 * Process multiple audio files
 */
export const processMultipleFiles = async (formData) => {
  try {
    const response = await apiClient.post('/asr/process-multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Multiple files processing failed:', error);
    throw new Error(error.response?.data?.detail || 'Batch processing failed');
  }
};

/**
 * Generate download URL for a file
 */
export const getDownloadUrl = (filePath) => {
  return `${API_BASE_URL}/asr/download/${encodeURIComponent(filePath)}`;
};

/**
 * Generate download URL for a bundle
 */
export const getBundleDownloadUrl = (taskId) => {
  return `${API_BASE_URL}/asr/download-bundle/${taskId}`;
};

/**
 * Start scanning a path for media files
 */
export const startScan = async (scanRequest) => {
  try {
    const response = await apiClient.post('/asr/scan/start', scanRequest);
    return response.data;
  } catch (error) {
    console.error('Failed to start scan:', error);
    throw new Error(error.response?.data?.detail || 'Failed to start scan');
  }
};

/**
 * Get scan status
 */
export const getScanStatus = async (scanId) => {
  try {
    const response = await apiClient.get(`/asr/scan/status/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get scan status:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get scan status');
  }
};

/**
 * Get scan result
 */
export const getScanResult = async (scanId) => {
  try {
    const response = await apiClient.get(`/asr/scan/result/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get scan result:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get scan result');
  }
};

/**
 * Get all scans
 */
export const getAllScans = async () => {
  try {
    const response = await apiClient.get('/asr/scan/all');
    return response.data;
  } catch (error) {
    console.error('Failed to get all scans:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get all scans');
  }
};

/**
 * Cancel a scan
 */
export const cancelScan = async (scanId) => {
  try {
    const response = await apiClient.post(`/asr/scan/cancel/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to cancel scan:', error);
    throw new Error(error.response?.data?.detail || 'Failed to cancel scan');
  }
};

/**
 * Get scan configuration
 */
export const getScanConfig = async () => {
  try {
    const response = await apiClient.get('/asr/scan/config');
    return response.data;
  } catch (error) {
    console.error('Failed to get scan config:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get scan config');
  }
};

/**
 * Browse a directory to get subdirectories and media files
 */
export const browseDirectory = async (path = '/') => {
  try {
    const response = await apiClient.get('/asr/scan/browse', { params: { path } });
    return response.data;
  } catch (error) {
    console.error('Failed to browse directory:', error);
    throw new Error(error.response?.data?.detail || 'Failed to browse directory');
  }
};

/**
 * Get detailed information about a specific path
 */
export const getPathInfo = async (path) => {
  try {
    const response = await apiClient.get('/asr/scan/path-info', { params: { path } });
    return response.data;
  } catch (error) {
    console.error('Failed to get path info:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get path info');
  }
};

export default apiClient;
