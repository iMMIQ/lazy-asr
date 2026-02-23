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
  VADProvidersResponse
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
 * Fetch available VAD providers from backend
 */
export async function fetchVADProviders(): Promise<VADProvidersResponse> {
  try {
    const response = await apiClient.get<VADProvidersResponse>('/vad/providers');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch VAD providers:', error);
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

export default apiClient;
