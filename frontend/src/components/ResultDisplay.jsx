import React from 'react';
import { useTranslation } from 'react-i18next';
import { getDownloadUrl, getBundleDownloadUrl } from '../services/api';
import { Download, FileText, CheckCircle2, XCircle, Clock, Database, AlertCircle } from 'lucide-react';

/**
 * Result display component for both single and multiple file processing results
 */
const ResultDisplay = ({
  result,
  multiFileResult,
  onDownload,
  onBundleDownload
}) => {
  const { t } = useTranslation();

  const StatItem = ({ icon: Icon, label, value }) => (
    <li>
      <span className="stat-label">
        <Icon size={16} className="stat-icon" />
        {label}
      </span>
      <span className="stat-value">{value}</span>
    </li>
  );

  const handleDownload = (filePath) => {
    const downloadUrl = getDownloadUrl(filePath);
    window.open(downloadUrl, '_blank');
  };

  const handleBundleDownload = (taskId) => {
    const downloadUrl = getBundleDownloadUrl(taskId);
    window.open(downloadUrl, '_blank');
  };

  const renderSingleResult = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h2>{t('results.title')}</h2>
        <div className="result-content">
          <p>{result.message}</p>

          {result.stats && (
            <div className="stats">
              <h3>
                <Database size={20} className="stats-icon" />
                {t('results.stats')}
              </h3>
              <ul>
                <StatItem icon={FileText} label={t('stats.totalSegments')} value={result.stats.total_segments} />
                <StatItem icon={CheckCircle2} label={t('stats.successfulTranscriptions')} value={result.stats.successful_transcriptions} />
                <StatItem icon={XCircle} label={t('stats.failedSegments')} value={result.stats.failed_segments} />
                <StatItem icon={AlertCircle} label={t('stats.emptySegments')} value={result.stats.empty_segments} />
                <StatItem icon={FileText} label={t('stats.totalSubtitles')} value={result.stats.total_subtitles} />
              </ul>
            </div>
          )}

          {result.segments && result.segments.length > 0 && (
            <div className="segments-preview">
              <h3>
                <Clock size={20} className="preview-icon" />
                {t('results.preview')}
              </h3>
              <div className="segments-list">
                {result.segments.map((segment, index) => (
                  <div key={index} className="segment-item">
                    <div className="segment-time">
                      <Clock size={14} className="time-icon" />
                      {segment.start} {'-->'} {segment.end}
                    </div>
                    <div className="segment-text">
                      {segment.text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.output_files && (
            <div className="download-buttons">
              <h3>{t('results.downloadFiles')}</h3>

              {/* Bundle download button - show when multiple formats are selected */}
              {Object.keys(result.output_files).length > 1 && result.task_id && (
                <button
                  onClick={() => handleBundleDownload(result.task_id)}
                  className="download-button bundle-download-button"
                >
                  <Download size={18} />
                  {t('buttons.downloadBundle')} ({Object.keys(result.output_files).length})
                </button>
              )}

              {/* Individual download buttons */}
              {Object.entries(result.output_files).map(([format, filePath]) => (
                <button
                  key={format}
                  onClick={() => handleDownload(filePath)}
                  className="download-button"
                >
                  <Download size={18} />
                  {t('buttons.download')} {format.toUpperCase()}
                </button>
              ))}
            </div>
          )}

          {/* Backward compatibility: show SRT download button if output_files is not available */}
          {!result.output_files && result.srt_file_path && (
            <button
              onClick={() => handleDownload(result.srt_file_path)}
              className="download-button"
            >
              <Download size={18} />
              {t('buttons.downloadSRT')}
            </button>
          )}
        </div>
      </div>
    );
  };

  const renderMultiFileResult = () => {
    if (!multiFileResult) return null;

    return (
      <div className="result-section">
        <h2>{t('results.batchTitle')}</h2>
        <div className="result-content">
          <p>{multiFileResult.message}</p>

          {multiFileResult.overall_stats && (
            <div className="stats">
              <h3>
                <Database size={20} className="stats-icon" />
                {t('results.overallStats')}
              </h3>
              <ul>
                <StatItem icon={FileText} label={t('stats.totalFiles')} value={multiFileResult.overall_stats.total_files} />
                <StatItem icon={CheckCircle2} label={t('stats.successfulFiles')} value={multiFileResult.overall_stats.successful_files} />
                <StatItem icon={XCircle} label={t('stats.failedFiles')} value={multiFileResult.overall_stats.failed_files} />
                <StatItem icon={FileText} label={t('stats.totalSubtitles')} value={multiFileResult.overall_stats.total_subtitles} />
                <StatItem icon={Clock} label={t('stats.totalSegments')} value={multiFileResult.overall_stats.total_segments} />
              </ul>
            </div>
          )}

          <div className="file-results">
            <h3>{t('results.fileDetails')}</h3>
            {multiFileResult.file_results.map((fileResult, index) => (
              <div key={index} className={`file-result ${fileResult.success ? 'success' : 'error'}`}>
                <h4>
                  {fileResult.success ? (
                    <CheckCircle2 size={20} className="success-icon" />
                  ) : (
                    <XCircle size={20} className="error-icon" />
                  )}
                  <span>{fileResult.filename}</span>
                </h4>
                <p>{fileResult.message}</p>

                {fileResult.success && fileResult.output_files && (
                  <div className="file-download-buttons">
                    {Object.entries(fileResult.output_files).map(([format, filePath]) => (
                      <button
                        key={format}
                        onClick={() => handleDownload(filePath)}
                        className="download-button small"
                      >
                        <Download size={16} />
                        {t('buttons.download')} {format.toUpperCase()}
                      </button>
                    ))}
                    {fileResult.task_id && (
                      <button
                        onClick={() => handleBundleDownload(fileResult.task_id)}
                        className="download-button small bundle"
                      >
                        <Download size={16} />
                        {t('buttons.downloadBundle')}
                      </button>
                    )}
                  </div>
                )}

                {fileResult.stats && (
                  <div className="file-stats">
                    <small>
                      {t('stats.totalSubtitles')}: {fileResult.stats.total_subtitles} |
                      {t('stats.totalSegments')}: {fileResult.stats.total_segments} |
                      {t('stats.successfulTranscriptions')}: {fileResult.stats.successful_transcriptions} |
                      {t('stats.failedSegments')}: {fileResult.stats.failed_segments}
                    </small>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {renderSingleResult()}
      {renderMultiFileResult()}
    </>
  );
};

export default ResultDisplay;
