import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useConfig } from '../context/ConfigContext';
import { startScan, getScanResult, cancelScan, getScanConfig } from '../services/api';
import type { ScanRequest, ScanStatusResponse, ScanResult, LanguageCode, ScanProgressData } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';
import { isScanProgressData } from '../types/websocket';
import ConfigPanel from './ConfigPanel';
import FolderSelector from './FolderSelector';
import './PathScanner.css';

/** Scan configuration from API */
interface ScanConfig {
  scan_paths?: string[];
  [key: string]: string | string[] | undefined;
}

/** Extended scan status with message */
interface ExtendedScanStatus extends ScanStatusResponse {
  message?: string;
}

/**
 * Path Scanner Component
 * Handles scanning directories for media files and batch ASR processing
 */
export function PathScanner(): React.ReactElement {
  const { t } = useTranslation();
  const { state, actions } = useConfig();

  // Local state for scanner-specific features
  const [scanPath, setScanPath] = useState<string>('');
  const [showFolderSelector, setShowFolderSelector] = useState(false);
  const [activeScanId, setActiveScanId] = useState<string | null>(null);
  const [scanStatus, setScanStatus] = useState<ExtendedScanStatus | null>(null);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanConfig, setScanConfig] = useState<ScanConfig | null>(null);

  // Fetch scan configuration on component mount
  useEffect(() => {
    fetchScanConfig();
  }, []);

  // WebSocket connection for real-time updates
  const {
    status: wsStatus,
    connected: wsConnected,
    lastStatus: wsLastStatus,
    error: wsError,
  } = useWebSocket(activeScanId, {
    autoReconnect: true,
    maxReconnectAttempts: 5,
    reconnectDelay: 3000,
  });

  // Update scan status from WebSocket messages
  useEffect(() => {
    if (wsLastStatus && wsConnected && isScanProgressData(wsLastStatus)) {
      const scanData: ScanProgressData = wsLastStatus;
      setScanStatus({
        scan_id: scanData.scan_id,
        status: scanData.status,
        progress: scanData.progress,
        total_files: scanData.total_files,
        processed_files: scanData.processed_files,
        failed_files: scanData.failed_files,
        current_file: scanData.current_file,
        message: scanData.error || 'Processing...',
      });

      // Update scanning state based on WebSocket status
      if (scanData.status === 'completed' || scanData.status === 'failed' || scanData.status === 'cancelled') {
        setIsScanning(false);
        if (scanData.status === 'completed') {
          fetchScanResult(scanData.scan_id);
        }
      }
    }
  }, [wsLastStatus, wsConnected]);

  const fetchScanConfig = async () => {
    try {
      const config = await getScanConfig();
      const scanConfig = config as ScanConfig;
      setScanConfig(scanConfig);

      // Set default path if available
      if (scanConfig.scan_paths && scanConfig.scan_paths.length > 0) {
        setScanPath(scanConfig.scan_paths[0]);
      }
    } catch (err) {
      console.error('Failed to fetch scan config:', err);
    }
  };

  const fetchScanResult = async (scanId: string) => {
    try {
      const result = await getScanResult(scanId);
      setScanResult(result);
    } catch (err) {
      console.error('Failed to fetch scan result:', err);
    }
  };

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!scanPath.trim()) {
      setError('Please enter a valid path');
      return;
    }

    try {
      setError(null);
      setIsScanning(true);
      actions.setProcessing(true);

      const scanRequest: ScanRequest = {
        path: scanPath,
        recursive: state.recursive,
        max_files: state.maxFiles,
        file_patterns: [],
        ...(state.asrMethod && { asr_method: state.asrMethod }),
        ...(state.vadMethod && { vad_method: state.vadMethod }),
        output_formats: state.outputFormats
      };

      const response = await startScan(scanRequest);
      setActiveScanId(response.scan_id);
      setScanStatus({
        scan_id: response.scan_id,
        status: 'idle',
        total_files: 0,
        processed_files: 0,
        progress: 0,
        message: 'Starting scan...',
        failed_files: 0
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsScanning(false);
      actions.setProcessing(false);
    }
  };

  const handleCancelScan = async () => {
    if (!activeScanId) return;

    try {
      await cancelScan(activeScanId);
      setIsScanning(false);
      actions.setProcessing(false);
      setScanStatus(prev => prev ? ({
        ...prev,
        status: 'cancelled',
        message: 'Scan cancelled by user'
      }) : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const resetScan = () => {
    setActiveScanId(null);
    setScanStatus(null);
    setScanResult(null);
    setIsScanning(false);
    setError(null);
    setShowFolderSelector(false);
  };

  const handlePathSelect = (path: string) => {
    setScanPath(path);
    setShowFolderSelector(false);
  };

  // Format progress bar
  const getProgressBarStyle = () => {
    if (!scanStatus) return { width: '0%' };
    return { width: `${scanStatus.progress}%` };
  };

  return (
    <div className="path-scanner">
      <div className="header-row">
        <h2>{t('pathScanner.title')}</h2>
        {/* Connection Status Indicator */}
        <div
          data-testid="connection-status"
          className={`connection-status ${wsConnected ? 'connected' : 'disconnected'}`}
          title={`Connection: ${wsStatus}${wsError ? ` - ${wsError}` : ''}`}
        >
          <span className="status-dot"></span>
          <span className="status-text">
            {wsConnected ? 'Live' : wsStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Scan Configuration Form */}
      <div className="scan-status-card">
        <form onSubmit={handleStartScan}>
          <div className="form-group">
            <label>{t('pathScanner.scanPath')}</label>
            <div className="path-input-group">
              <input
                type="text"
                value={scanPath}
                onChange={(e) => setScanPath(e.target.value)}
                placeholder="/path/to/media/files"
                disabled={isScanning}
              />
              <button
                type="button"
                className="browse-folder-btn"
                onClick={() => setShowFolderSelector(!showFolderSelector)}
                disabled={isScanning}
                title={t('folderSelector.title')}
              >
                📁 {showFolderSelector ? t('folderSelector.close') : t('folderSelector.browse')}
              </button>
            </div>
            {scanConfig && scanConfig.scan_paths && scanConfig.scan_paths.length > 0 && (
              <p className="text-sm text-muted mt-1">
                {t('pathScanner.suggestedPaths')}: {scanConfig.scan_paths.join(', ')}
              </p>
            )}
          </div>

          {/* Folder Selector */}
          {showFolderSelector && (
            <div className="folder-selector-container">
              <FolderSelector
                onPathSelect={handlePathSelect}
                selectedPath={scanPath}
                disabled={isScanning}
              />
            </div>
          )}

          {/* Configuration Panel */}
          <ConfigPanel
            asrMethod={state.asrMethod}
            availablePlugins={state.availablePlugins}
            outputFormats={state.outputFormats}
            minSpeechDuration={state.minSpeechDuration}
            minSilenceDuration={state.minSilenceDuration}
            asrLanguage={state.asrLanguage}
            asrApiUrl={state.asrApiUrl}
            asrApiKey={state.asrApiKey}
            asrModel={state.asrModel}
            vadMethod={state.vadMethod}
            availableVADProviders={state.availableVADProviders}
            onMethodChange={(e) => actions.setAsrMethod(e.target.value)}
            onFormatChange={actions.toggleOutputFormat}
            onVadMethodChange={(method) => actions.setVadMethod(method)}
            onVadConfigChange={(field, value) => {
              if (field === 'minSpeechDuration') {
                actions.setMinSpeechDuration(value);
              } else if (field === 'minSilenceDuration') {
                actions.setMinSilenceDuration(value);
              }
            }}
            onAsrConfigChange={(field, value) => {
              switch (field) {
                case 'asrApiUrl':
                  actions.setAsrApiUrl(value);
                  break;
                case 'asrApiKey':
                  actions.setAsrApiKey(value);
                  break;
                case 'asrModel':
                  actions.setAsrModel(value);
                  break;
                case 'asrLanguage':
                  actions.setAsrLanguage(value as LanguageCode);
                  break;
                default:
                  break;
              }
            }}
            showVadConfig={true}
            showAsrAdvancedConfig={true}
            isProcessing={isScanning}
            showMaxFiles={true}
            maxFiles={state.maxFiles}
            onMaxFilesChange={(value) => actions.setMaxFiles(value)}
            showRecursiveOption={true}
            recursive={state.recursive}
            onRecursiveChange={actions.setRecursive}
          />


          {error && (
            <div className="scanner-error">
              {error}
            </div>
          )}

          <div className="scan-action-buttons">
            <button
              type="submit"
              disabled={isScanning || !scanPath.trim()}
              className={`scan-button ${isScanning || !scanPath.trim() ? 'disabled' : ''}`}
            >
              {isScanning ? t('pathScanner.scanning') : t('pathScanner.startScan')}
            </button>

            {isScanning && (
              <button
                type="button"
                onClick={handleCancelScan}
                className="scan-button cancel"
              >
                {t('pathScanner.cancelScan')}
              </button>
            )}

            {scanResult && (
              <button
                type="button"
                onClick={resetScan}
                className="scan-button new"
              >
                {t('pathScanner.newScan')}
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Scan Status Display */}
      {scanStatus && (
        <div className="scan-status-card">
          <h3>{t('pathScanner.scanStatus')}</h3>

          <div className="mb-4">
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">
                {scanStatus.status.charAt(0).toUpperCase() + scanStatus.status.slice(1)}
              </span>
              <span className="text-sm font-medium">{scanStatus.progress}%</span>
            </div>
            <div className="progress-bar-container">
              <div
                className={`progress-bar ${scanStatus.status}`}
                style={getProgressBarStyle()}
              ></div>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="value">{scanStatus.total_files}</div>
              <div className="label">{t('pathScanner.totalFiles')}</div>
            </div>

            <div className="stat-card">
              <div className="value">{scanStatus.processed_files}</div>
              <div className="label">{t('pathScanner.processedFiles')}</div>
            </div>

            <div className="stat-card">
              <div className="value">{scanStatus.failed_files}</div>
              <div className="label">{t('pathScanner.failedFiles')}</div>
            </div>
          </div>

          <div className="mb-4">
            <p>
              <span className="font-medium">{t('pathScanner.currentFile')}:</span>{' '}
              {scanStatus.current_file || t('pathScanner.noFileProcessing')}
            </p>
            <p>
              <span className="font-medium">{t('pathScanner.message')}:</span> {scanStatus.message}
            </p>
          </div>

          {scanStatus.scan_id && (
            <p className="text-sm text-muted">
              {t('pathScanner.scanId')}: {scanStatus.scan_id}
            </p>
          )}
        </div>
      )}

      {/* Scan Results Display */}
      {scanResult && (
        <div className="scan-status-card">
          <h3>{t('pathScanner.scanResults')}</h3>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="value">{scanResult.total_files}</div>
              <div className="label">{t('pathScanner.totalFiles')}</div>
            </div>

            <div className="stat-card">
              <div className="value">{scanResult.processed_files}</div>
              <div className="label">{t('pathScanner.processedFiles')}</div>
            </div>

            <div className="stat-card">
              <div className="value">{scanResult.failed_files}</div>
              <div className="label">{t('pathScanner.failedFiles')}</div>
            </div>

            <div className="stat-card">
              <div className="value">{((scanResult as any).success_rate * 100).toFixed(1)}%</div>
              <div className="label">{t('pathScanner.successRate')}</div>
            </div>
          </div>

          <div className="mb-4">
            <p>
              <span className="font-medium">{t('pathScanner.duration')}:</span>{' '}
              {(scanResult as any).duration_seconds.toFixed(1)} {t('pathScanner.seconds')}
            </p>
            <p>
              <span className="font-medium">{t('pathScanner.startTime')}:</span>{' '}
              {new Date((scanResult as any).start_time).toLocaleString()}
            </p>
            <p>
              <span className="font-medium">{t('pathScanner.endTime')}:</span>{' '}
              {new Date((scanResult as any).end_time).toLocaleString()}
            </p>
          </div>

          {/* Results Summary */}
          {scanResult.results && scanResult.results.length > 0 && (
            <div className="mt-6">
              <h4>{t('pathScanner.resultsSummary')}</h4>
              <div className="overflow-x-auto">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>{t('pathScanner.fileIndex')}</th>
                      <th>{t('pathScanner.status')}</th>
                      <th>{t('pathScanner.message')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scanResult.results.slice(0, 10).map((result, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>
                          <span className={`status-badge ${result.success ? 'success' : 'failed'}`}>
                            {result.success ? t('pathScanner.success') : t('pathScanner.failed')}
                          </span>
                        </td>
                        <td>{(result as any).message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {scanResult.results.length > 10 && (
                <p className="text-sm text-muted mt-2">
                  {t('pathScanner.showingFirst10')} {scanResult.results.length} {t('pathScanner.results')}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PathScanner;
