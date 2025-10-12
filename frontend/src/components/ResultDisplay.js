import React from 'react';
import { useTranslation } from 'react-i18next';
import { getDownloadUrl, getBundleDownloadUrl } from '../services/api';

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
              <h3>{t('results.stats')}</h3>
              <ul>
                <li>{t('stats.totalSegments')}: {result.stats.total_segments}</li>
                <li>{t('stats.successfulTranscriptions')}: {result.stats.successful_transcriptions}</li>
                <li>{t('stats.failedSegments')}: {result.stats.failed_segments}</li>
                <li>{t('stats.emptySegments')}: {result.stats.empty_segments}</li>
                <li>{t('stats.totalSubtitles')}: {result.stats.total_subtitles}</li>
              </ul>
            </div>
          )}

          {result.segments && result.segments.length > 0 && (
            <div className="segments-preview">
              <h3>{t('results.preview')}</h3>
              <div className="segments-list">
                {result.segments.map((segment, index) => (
                  <div key={index} className="segment-item">
                    <div className="segment-time">
                      {segment.start} --> {segment.end}
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
              <h3>{t('results.overallStats')}</h3>
              <ul>
                <li>{t('stats.totalFiles')}: {multiFileResult.overall_stats.total_files}</li>
                <li>{t('stats.successfulFiles')}: {multiFileResult.overall_stats.successful_files}</li>
                <li>{t('stats.failedFiles')}: {multiFileResult.overall_stats.failed_files}</li>
                <li>{t('stats.totalSubtitles')}: {multiFileResult.overall_stats.total_subtitles}</li>
                <li>{t('stats.totalSegments')}: {multiFileResult.overall_stats.total_segments}</li>
              </ul>
            </div>
          )}

          <div className="file-results">
            <h3>{t('results.fileDetails')}</h3>
            {multiFileResult.file_results.map((fileResult, index) => (
              <div key={index} className={`file-result ${fileResult.success ? 'success' : 'error'}`}>
                <h4>
                  {fileResult.success ? '✅' : '❌'} {fileResult.filename}
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
                        {t('buttons.download')} {format.toUpperCase()}
                      </button>
                    ))}
                    {fileResult.task_id && (
                      <button
                        onClick={() => handleBundleDownload(fileResult.task_id)}
                        className="download-button small bundle"
                      >
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
