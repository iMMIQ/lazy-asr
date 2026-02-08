import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useConfig } from '../context/ConfigContext';
import { startScan, getScanStatus, getScanResult, cancelScan, getScanConfig } from '../services/api';
import type { ScanRequest, ScanStatusResponse, ScanResult, LanguageCode } from '../types';
import ConfigPanel from './ConfigPanel';
import FolderSelector from './FolderSelector';
import './PathScanner.css';

/** Scan configuration from API */
interface ScanConfig {
  scan_paths?: string[];
  [key: string]: string | string[] | undefined;
}

/** Extended scan status with message */
interface ExtendedScanStatus extends Omit<ScanStatusResponse, 'failed_files'> {
  message?: string;
  failed_files?: number;
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

  // Poll scan status if there's an active scan
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval> | null = null;

    if (activeScanId && isScanning) {
      intervalId = setInterval(() => {
        fetchScanStatus(activeScanId);
      }, 2000); // Poll every 2 seconds
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [activeScanId, isScanning]);

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

  const fetchScanStatus = async (scanId: string) => {
    try {
      const status = await getScanStatus(scanId);
      setScanStatus(status as ExtendedScanStatus);

      // Update scanning state
      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        setIsScanning(false);

        // Fetch result if completed
        if (status.status === 'completed') {
          fetchScanResult(scanId);
        }
      }
    } catch (err) {
      console.error('Failed to fetch scan status:', err);
      if (err instanceof Error && err.message.includes('Scan not found')) {
        setIsScanning(false);
        setActiveScanId(null);
      }
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
        file_patterns: []
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
      <h2>{t('pathScanner.title')}</h2>

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
            onMethodChange={(e) => actions.setAsrMethod(e.target.value)}
            onFormatChange={actions.toggleOutputFormat}
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
