import axios, { type AxiosInstance } from 'axios';
import type {
  ASRPlugin,
  ApiErrorResponse,
  ProcessResult,
  ScanRequest,
  ScanResult,
  ScanStatusResponse,
  DirectoryBrowseResult,
  PathInfo,
  MonitorConfig,
  MonitorListResponse,
  MonitorServiceStatus,
  DatabaseStatus
} from '../types';

// Use relative path for Vite proxy compatibility
const API_BASE_URL = '/api/v1';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 600 seconds timeout
});

/**
 * Extract error message from API error response
 */
function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    return data?.detail || data?.message || error.message || 'Request failed';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

/**
 * Fetch available ASR plugins from backend
 */
export async function fetchPlugins(): Promise<{ plugins: ASRPlugin[] }> {
  try {
    const response = await apiClient.get<{ plugins: ASRPlugin[] }>('/asr/plugins');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch plugins:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Process single audio file
 */
export async function processSingleFile(formData: FormData): Promise<ProcessResult[]> {
  try {
    const response = await apiClient.post<ProcessResult[]>('/asr/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Single file processing failed:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Process multiple audio files
 */
export async function processMultipleFiles(formData: FormData): Promise<ProcessResult[]> {
  try {
    const response = await apiClient.post<ProcessResult[]>('/asr/process-multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Multiple files processing failed:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Generate download URL for a file
 */
export function getDownloadUrl(filePath: string): string {
  return `${API_BASE_URL}/asr/download/${encodeURIComponent(filePath)}`;
}

/**
 * Generate download URL for a bundle
 */
export function getBundleDownloadUrl(taskId: string): string {
  return `${API_BASE_URL}/asr/download-bundle/${taskId}`;
}

/**
 * Start scanning a path for media files
 */
export async function startScan(scanRequest: ScanRequest): Promise<{ scan_id: string }> {
  try {
    const response = await apiClient.post<{ scan_id: string }>('/asr/scan/start', scanRequest);
    return response.data;
  } catch (error) {
    console.error('Failed to start scan:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get scan status
 */
export async function getScanStatus(scanId: string): Promise<ScanStatusResponse> {
  try {
    const response = await apiClient.get<ScanStatusResponse>(`/asr/scan/status/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get scan status:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get scan result
 */
export async function getScanResult(scanId: string): Promise<ScanResult> {
  try {
    const response = await apiClient.get<ScanResult>(`/asr/scan/result/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get scan result:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get all scans
 */
export async function getAllScans(): Promise<{ scans: ScanResult[] }> {
  try {
    const response = await apiClient.get<{ scans: ScanResult[] }>('/asr/scan/all');
    return response.data;
  } catch (error) {
    console.error('Failed to get all scans:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Cancel a scan
 */
export async function cancelScan(scanId: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>(`/asr/scan/cancel/${scanId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to cancel scan:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get scan configuration
 */
export async function getScanConfig(): Promise<{ max_files?: number; [key: string]: unknown }> {
  try {
    const response = await apiClient.get('/asr/scan/config');
    return response.data;
  } catch (error) {
    console.error('Failed to get scan config:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Browse a directory to get subdirectories and media files
 */
export async function browseDirectory(path: string = '/'): Promise<DirectoryBrowseResult> {
  try {
    const response = await apiClient.get<DirectoryBrowseResult>('/asr/scan/browse', {
      params: { path }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to browse directory:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get detailed information about a specific path
 */
export async function getPathInfo(path: string): Promise<PathInfo> {
  try {
    const response = await apiClient.get<PathInfo>('/asr/scan/path-info', {
      params: { path }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get path info:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Monitor Management APIs
 */

/**
 * Create a new monitor configuration
 */
export async function createMonitor(config: MonitorConfig): Promise<{ monitor_id: string }> {
  try {
    const response = await apiClient.post<{ monitor_id: string }>('/asr/monitor/create', config);
    return response.data;
  } catch (error) {
    console.error('Failed to create monitor:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get all monitor configurations
 */
export async function getAllMonitors(activeOnly = false): Promise<MonitorListResponse> {
  try {
    const response = await apiClient.get<MonitorListResponse>('/asr/monitor/all', {
      params: { active_only: activeOnly }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get monitors:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get monitor by ID
 */
export async function getMonitor(monitorId: string): Promise<MonitorConfig> {
  try {
    const response = await apiClient.get<MonitorConfig>(`/asr/monitor/${monitorId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get monitor:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Update monitor configuration
 */
export async function updateMonitor(
  monitorId: string,
  config: Partial<MonitorConfig>
): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.put<{ success: boolean }>(
      `/asr/monitor/${monitorId}`,
      config
    );
    return response.data;
  } catch (error) {
    console.error('Failed to update monitor:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Delete monitor configuration
 */
export async function deleteMonitor(monitorId: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.delete<{ success: boolean }>(`/asr/monitor/${monitorId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to delete monitor:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Toggle monitor active status
 */
export async function toggleMonitor(
  monitorId: string,
  isActive: boolean
): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>(
      `/asr/monitor/${monitorId}/toggle`,
      null,
      {
        params: { is_active: isActive }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to toggle monitor:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get monitor service status
 */
export async function getMonitorServiceStatus(): Promise<MonitorServiceStatus> {
  try {
    const response = await apiClient.get<MonitorServiceStatus>('/asr/monitor/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get monitor service status:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Start monitor service
 */
export async function startMonitorService(): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>('/asr/monitor/service/start');
    return response.data;
  } catch (error) {
    console.error('Failed to start monitor service:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Stop monitor service
 */
export async function stopMonitorService(): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>('/asr/monitor/service/stop');
    return response.data;
  } catch (error) {
    console.error('Failed to stop monitor service:', error);
    throw new Error(getErrorMessage(error));
  }
}

/**
 * Get database status
 */
export async function getDatabaseStatus(): Promise<DatabaseStatus> {
  try {
    const response = await apiClient.get<DatabaseStatus>('/asr/database/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get database status:', error);
    throw new Error(getErrorMessage(error));
  }
}

export default apiClient;
