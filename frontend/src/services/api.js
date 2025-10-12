import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
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

export default apiClient;
