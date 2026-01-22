import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import './MonitorManager.css';

/** Monitor configuration */
interface Monitor {
  id: string;
  name: string;
  path: string;
  recursive: boolean;
  asr_method: string;
  output_formats: string[] | string;
  auto_process: boolean;
  scan_interval: number;
  is_active: boolean;
  last_scan_time?: string;
}

/** Service status */
interface ServiceStatus {
  service_running: boolean;
  total_monitors: number;
  active_monitors: number;
}

/**
 * Monitor Manager Component
 * Manages file system monitors for automatic ASR processing
 */
export function MonitorManager(): React.ReactElement {
  const { t } = useTranslation();
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Load monitors and service status on mount
  useEffect(() => {
    loadMonitors();
    loadServiceStatus();
  }, []);

  const loadMonitors = async () => {
    try {
      const response = await api.get('/monitor/all');
      setMonitors(response.data.monitors || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load monitors:', err);
      setError(t('errors.processingFailed'));
      setLoading(false);
    }
  };

  const loadServiceStatus = async () => {
    try {
      const response = await api.get('/monitor/status');
      setServiceStatus(response.data);
    } catch (err) {
      console.error('Failed to load service status:', err);
    }
  };

  const handleStartService = async () => {
    try {
      await api.post('/monitor/service/start');
      loadServiceStatus();
    } catch (err) {
      console.error('Failed to start service:', err);
      setError(t('monitorManager.startService') + ' ' + t('errors.failed'));
    }
  };

  const handleStopService = async () => {
    try {
      await api.post('/monitor/service/stop');
      loadServiceStatus();
    } catch (err) {
      console.error('Failed to stop service:', err);
      setError(t('monitorManager.stopService') + ' ' + t('errors.failed'));
    }
  };

  const handleRenameMonitor = async (monitor: Monitor) => {
    const newName = prompt(t('monitorManager.editNamePrompt'), monitor.name);
    if (newName && newName.trim() !== '' && newName !== monitor.name) {
      try {
        await api.put(`/monitor/${monitor.id}`, {
          name: newName.trim(),
          path: monitor.path,
          recursive: monitor.recursive,
          asr_method: monitor.asr_method,
          output_formats: monitor.output_formats,
          auto_process: monitor.auto_process,
          scan_interval: monitor.scan_interval,
        });
        loadMonitors();
      } catch (err) {
        console.error('Failed to rename monitor:', err);
        setError(t('errors.processingFailed'));
      }
    }
  };

  const handleToggleMonitor = async (monitorId: string, currentStatus: boolean) => {
    try {
      await api.post(`/monitor/${monitorId}/toggle`, null, {
        params: { is_active: !currentStatus },
      });
      loadMonitors();
    } catch (err) {
      console.error('Failed to toggle monitor:', err);
      setError(t('errors.processingFailed'));
    }
  };

  const handleDeleteMonitor = async (monitorId: string) => {
    if (!window.confirm(t('monitorManager.confirmDelete'))) {
      return;
    }
    try {
      await api.delete(`/monitor/${monitorId}`);
      loadMonitors();
    } catch (err) {
      console.error('Failed to delete monitor:', err);
      setError(t('errors.processingFailed'));
    }
  };

  const formatInterval = (seconds: number): string => {
    if (seconds < 60) return `${seconds} ${t('monitorManager.seconds')}`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)} ${t('monitorManager.minutes')}`;
    return `${Math.floor(seconds / 3600)} ${t('monitorManager.hours')}`;
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return t('monitorManager.neverScanned');
    return new Date(dateString).toLocaleString();
  };

  const formatBoolean = (value: boolean): string => {
    return value ? (t('language.chinese') === '中文' ? '是' : 'Yes') : (t('language.chinese') === '中文' ? '否' : 'No');
  };

  if (loading) {
    return <div className="loading">{t('monitorManager.loading')}</div>;
  }

  return (
    <div className="monitor-manager">
      <div className="header">
        <h2>{t('monitorManager.title')}</h2>
        <div className="button-group">
          {serviceStatus?.service_running ? (
            <button className="btn btn-danger" onClick={handleStopService}>
              {t('monitorManager.stopService')}
            </button>
          ) : (
            <button className="btn btn-primary" onClick={handleStartService}>
              {t('monitorManager.startService')}
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className={`service-status ${serviceStatus?.service_running ? 'running' : 'stopped'}`}>
        <h3>
          <span className={`status-indicator ${serviceStatus?.service_running ? 'active' : 'inactive'}`} />
          {t('monitorManager.serviceStatus')}
        </h3>
        <div>
          <strong>{serviceStatus?.service_running ? t('monitorManager.running') : t('monitorManager.stopped')}</strong>
          {' '}| {t('monitorManager.totalMonitors')}: {serviceStatus?.total_monitors || 0}
          {' '}| {t('monitorManager.activeMonitors')}: {serviceStatus?.active_monitors || 0}
        </div>
      </div>

      <div className="monitor-list">
        {monitors.length === 0 ? (
          <div className="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3zM9 9h6v6H9z" />
            </svg>
            <p>{t('monitorManager.emptyState')}</p>
          </div>
        ) : (
          monitors.map((monitor) => (
            <div key={monitor.id} className="monitor-card">
              <div className="monitor-header">
                <div className="monitor-name">{monitor.name}</div>
                <div className={`monitor-status ${monitor.is_active ? 'active' : 'inactive'}`}>
                  {monitor.is_active ? t('monitorManager.active') : t('monitorManager.inactive')}
                </div>
              </div>

              <div className="monitor-info">
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.monitorPath')}</div>
                  <div className="info-value">{monitor.path}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.scanInterval')}</div>
                  <div className="info-value">{formatInterval(monitor.scan_interval)}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.asrMethod')}</div>
                  <div className="info-value">{monitor.asr_method}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.outputFormats')}</div>
                  <div className="info-value">
                    {Array.isArray(monitor.output_formats) ? monitor.output_formats.join(', ') : monitor.output_formats}
                  </div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.recursiveScan')}</div>
                  <div className="info-value">{formatBoolean(monitor.recursive)}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.autoProcess')}</div>
                  <div className="info-value">{formatBoolean(monitor.auto_process)}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">{t('monitorManager.lastScan')}</div>
                  <div className="info-value">{formatDate(monitor.last_scan_time)}</div>
                </div>
              </div>

              <div className="monitor-actions">
                <button className="btn btn-secondary" onClick={() => handleToggleMonitor(monitor.id, monitor.is_active)}>
                  {monitor.is_active ? t('monitorManager.disable') : t('monitorManager.enable')}
                </button>
                <button className="btn btn-secondary" onClick={() => handleRenameMonitor(monitor)}>
                  {t('monitorManager.rename')}
                </button>
                <button className="btn btn-danger" onClick={() => handleDeleteMonitor(monitor.id)}>
                  {t('monitorManager.delete')}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default MonitorManager;
