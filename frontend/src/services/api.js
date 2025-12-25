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

/**
 * Monitor Management APIs
 */

/**
 * Create a new monitor configuration
 */
export const createMonitor = async (config) => {
  try {
    const response = await apiClient.post('/asr/monitor/create', config);
    return response.data;
  } catch (error) {
    console.error('Failed to create monitor:', error);
    throw new Error(error.response?.data?.detail || 'Failed to create monitor');
  }
};

/**
 * Get all monitor configurations
 */
export const getAllMonitors = async (activeOnly = false) => {
  try {
    const response = await apiClient.get('/asr/monitor/all', {
      params: { active_only: activeOnly }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get monitors:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get monitors');
  }
};

/**
 * Get monitor by ID
 */
export const getMonitor = async (monitorId) => {
  try {
    const response = await apiClient.get(`/asr/monitor/${monitorId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get monitor:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get monitor');
  }
};

/**
 * Update monitor configuration
 */
export const updateMonitor = async (monitorId, config) => {
  try {
    const response = await apiClient.put(`/asr/monitor/${monitorId}`, config);
    return response.data;
  } catch (error) {
    console.error('Failed to update monitor:', error);
    throw new Error(error.response?.data?.detail || 'Failed to update monitor');
  }
};

/**
 * Delete monitor configuration
 */
export const deleteMonitor = async (monitorId) => {
  try {
    const response = await apiClient.delete(`/asr/monitor/${monitorId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to delete monitor:', error);
    throw new Error(error.response?.data?.detail || 'Failed to delete monitor');
  }
};

/**
 * Toggle monitor active status
 */
export const toggleMonitor = async (monitorId, isActive) => {
  try {
    const response = await apiClient.post(`/asr/monitor/${monitorId}/toggle`, null, {
      params: { is_active: isActive }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to toggle monitor:', error);
    throw new Error(error.response?.data?.detail || 'Failed to toggle monitor');
  }
};

/**
 * Get monitor service status
 */
export const getMonitorServiceStatus = async () => {
  try {
    const response = await apiClient.get('/asr/monitor/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get monitor service status:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get monitor service status');
  }
};

/**
 * Start monitor service
 */
export const startMonitorService = async () => {
  try {
    const response = await apiClient.post('/asr/monitor/service/start');
    return response.data;
  } catch (error) {
    console.error('Failed to start monitor service:', error);
    throw new Error(error.response?.data?.detail || 'Failed to start monitor service');
  }
};

/**
 * Stop monitor service
 */
export const stopMonitorService = async () => {
  try {
    const response = await apiClient.post('/asr/monitor/service/stop');
    return response.data;
  } catch (error) {
    console.error('Failed to stop monitor service:', error);
    throw new Error(error.response?.data?.detail || 'Failed to stop monitor service');
  }
};

/**
 * Persistent Scan APIs
 */

/**
 * Start persistent scan with database support
 */
export const startPersistentScan = async (scanRequest) => {
  try {
    const response = await apiClient.post('/asr/scan/persistent/start', scanRequest);
    return response.data;
  } catch (error) {
    console.error('Failed to start persistent scan:', error);
    throw new Error(error.response?.data?.detail || 'Failed to start persistent scan');
  }
};

/**
 * Get persistent scan status
 */
export const getPersistentScanStatus = async (scanId) => {
  try {
    const response = await apiClient.get(`/asr/scan/persistent/status/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get persistent scan status:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get persistent scan status');
  }
};

/**
 * Get all persistent scans
 */
export const getAllPersistentScans = async (limit = 50, offset = 0, status = null) => {
  try {
    const params = { limit, offset };
    if (status) params.status = status;
    const response = await apiClient.get('/asr/scan/persistent/all', { params });
    return response.data;
  } catch (error) {
    console.error('Failed to get persistent scans:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get persistent scans');
  }
};

/**
 * Cancel persistent scan
 */
export const cancelPersistentScan = async (scanId) => {
  try {
    const response = await apiClient.post(`/asr/scan/persistent/cancel/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to cancel persistent scan:', error);
    throw new Error(error.response?.data?.detail || 'Failed to cancel persistent scan');
  }
};

/**
 * Delete persistent scan
 */
export const deletePersistentScan = async (scanId) => {
  try {
    const response = await apiClient.delete(`/asr/scan/persistent/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to delete persistent scan:', error);
    throw new Error(error.response?.data?.detail || 'Failed to delete persistent scan');
  }
};

/**
 * Get media files for a persistent scan
 */
export const getPersistentScanFiles = async (scanId, limit = 100, offset = 0) => {
  try {
    const response = await apiClient.get(`/asr/scan/persistent/${scanId}/files`, {
      params: { limit, offset }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get persistent scan files:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get persistent scan files');
  }
};

/**
 * Get database status
 */
export const getDatabaseStatus = async () => {
  try {
    const response = await apiClient.get('/asr/database/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get database status:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get database status');
  }
};

export default apiClient;
