import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function App() {
  const { t, i18n } = useTranslation();
  const [audioFiles, setAudioFiles] = useState([]);
  const [asrMethod, setAsrMethod] = useState('');
  const [availablePlugins, setAvailablePlugins] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [multiFileResult, setMultiFileResult] = useState(null);
  const [error, setError] = useState(null);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [minSpeechDuration, setMinSpeechDuration] = useState(500);
  const [minSilenceDuration, setMinSilenceDuration] = useState(500);
  const [asrApiUrl, setAsrApiUrl] = useState('');
  const [asrApiKey, setAsrApiKey] = useState('');
  const [asrModel, setAsrModel] = useState('');
  const [asrLanguage, setAsrLanguage] = useState('auto'); // Default to auto detect
  const [outputFormats, setOutputFormats] = useState(['srt']); // Default to SRT for backward compatibility

  // Fetch available plugins on component mount
  useEffect(() => {
    fetchAvailablePlugins();
  }, []);

  const fetchAvailablePlugins = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/asr/plugins`);
      const plugins = response.data.plugins;
      const defaultMethod = response.data.default_method;
      setAvailablePlugins(plugins);
      
      // Set the default method from backend configuration
      if (defaultMethod && plugins.includes(defaultMethod)) {
        setAsrMethod(defaultMethod);
      } else if (plugins.length > 0 && !asrMethod) {
        // Fallback to first plugin if default is not available
        setAsrMethod(plugins[0]);
      }
    } catch (err) {
      console.error('Failed to fetch plugins:', err);
      setError('Failed to fetch available ASR methods');
    }
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setAudioFiles(files);
    setError(null);
    setResult(null);
    setMultiFileResult(null);
  };

  const removeFile = (index) => {
    const newFiles = [...audioFiles];
    newFiles.splice(index, 1);
    setAudioFiles(newFiles);
  };

  const handleMethodChange = (event) => {
    setAsrMethod(event.target.value);
  };

  const handleSingleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length !== 1) {
      setError(t('errors.selectSingleFile'));
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setMultiFileResult(null);

    try {
      const formData = new FormData();
      formData.append('audio_file', audioFiles[0]);
      formData.append('asr_method', asrMethod);
      
      // Add output formats
      formData.append('output_formats', outputFormats.join(','));

      // Add VAD parameters
      if (showAdvancedOptions) {
        formData.append('min_speech_duration', minSpeechDuration);
        formData.append('min_silence_duration', minSilenceDuration);

        // Add ASR configuration parameters
        if (asrApiUrl) formData.append('asr_api_url', asrApiUrl);
        if (asrApiKey) formData.append('asr_api_key', asrApiKey);
        if (asrModel) formData.append('asr_model', asrModel);
        // Add language parameter
        formData.append('language', asrLanguage);
      }

      const response = await axios.post(`${API_BASE_URL}/asr/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      console.error('Processing failed:', err);
      setError(err.response?.data?.detail || t('errors.processingFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleMultipleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length === 0) {
      setError(t('errors.selectFiles'));
      return;
    }

    if (audioFiles.length > 10) {
      setError(t('errors.maxFilesExceeded'));
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setMultiFileResult(null);

    try {
      const formData = new FormData();
      
      // Add all files
      audioFiles.forEach(file => {
        formData.append('audio_files', file);
      });
      
      formData.append('asr_method', asrMethod);
      formData.append('output_formats', outputFormats.join(','));

      // Add VAD parameters
      if (showAdvancedOptions) {
        formData.append('min_speech_duration', minSpeechDuration);
        formData.append('min_silence_duration', minSilenceDuration);

        // Add ASR configuration parameters
        if (asrApiUrl) formData.append('asr_api_url', asrApiUrl);
        if (asrApiKey) formData.append('asr_api_key', asrApiKey);
        if (asrModel) formData.append('asr_model', asrModel);
        // Add language parameter
        formData.append('language', asrLanguage);
      }

      const response = await axios.post(`${API_BASE_URL}/asr/process-multiple`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMultiFileResult(response.data);
    } catch (err) {
      console.error('Batch processing failed:', err);
      setError(err.response?.data?.detail || t('errors.batchProcessingFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = (filePath) => {
    const downloadUrl = `${API_BASE_URL}/asr/download/${encodeURIComponent(filePath)}`;
    window.open(downloadUrl, '_blank');
  };

  const handleBundleDownload = (taskId) => {
    const downloadUrl = `${API_BASE_URL}/asr/download-bundle/${taskId}`;
    window.open(downloadUrl, '_blank');
  };

  const handleFormatChange = (format) => {
    setOutputFormats(prev => {
      if (prev.includes(format)) {
        // Remove format if already selected
        return prev.filter(f => f !== format);
      } else {
        // Add format if not selected
        return [...prev, format];
      }
    });
  };

  // Language switcher function
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>{t('app.title')}</h1>
        <p>{t('app.description')}</p>
        <div className="language-switcher">
          <button 
            onClick={() => changeLanguage('zh')} 
            className={i18n.language === 'zh' ? 'active' : ''}
          >
            {t('language.chinese')}
          </button>
          <button 
            onClick={() => changeLanguage('en')} 
            className={i18n.language === 'en' ? 'active' : ''}
          >
            {t('language.english')}
          </button>
        </div>
      </header>

      <main className="App-main">
        <div className="processing-form">
          <div className="form-group">
            <label htmlFor="audioFile">{t('form.uploadAudio')}</label>
            <input
              type="file"
              id="audioFile"
              accept="audio/*"
              multiple
              onChange={handleFileChange}
              disabled={isProcessing}
            />
            <small>{t('form.maxFiles')}</small>
          </div>

          {audioFiles.length > 0 && (
            <div className="file-list">
              <h4>{t('form.selectedFiles')} ({audioFiles.length}):</h4>
              <ul>
                {audioFiles.map((file, index) => (
                  <li key={index} className="file-item">
                    <span>{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      disabled={isProcessing}
                      className="remove-file-btn"
                    >
                      {t('form.removeFile')}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="asrMethod">{t('form.selectASR')}</label>
            <select
              id="asrMethod"
              value={asrMethod}
              onChange={handleMethodChange}
              disabled={isProcessing}
            >
              {availablePlugins.map((plugin) => (
                <option key={plugin} value={plugin}>
                  {plugin}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>{t('form.selectOutputFormats')}</label>
            <div className="format-checkboxes">
              {['srt', 'vtt', 'lrc', 'txt'].map((format) => (
                <label 
                  key={format} 
                  className={`format-checkbox ${outputFormats.includes(format) ? 'selected' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={outputFormats.includes(format)}
                    onChange={() => handleFormatChange(format)}
                    disabled={isProcessing}
                  />
                  <span className="format-label">{format.toUpperCase()}</span>
                </label>
              ))}
            </div>
            <small>{t('form.outputFormatsDescription')}</small>
          </div>

          {/* Advanced Options */}
          <div className="advanced-options">
            <button
              type="button"
              className="advanced-toggle"
              onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            >
              {showAdvancedOptions ? '▼' : '▶'} {t('form.advancedOptions')}
            </button>

            {showAdvancedOptions && (
              <div className="advanced-content">
                <h3>{t('form.vadConfig')}</h3>
                <div className="form-group">
                  <label htmlFor="minSpeechDuration">{t('form.minSpeechDuration')}</label>
                  <input
                    type="number"
                    id="minSpeechDuration"
                    value={minSpeechDuration}
                    onChange={(e) => setMinSpeechDuration(parseInt(e.target.value) || 500)}
                    min="100"
                    max="5000"
                    step="100"
                    disabled={isProcessing}
                  />
                  <small>{t('form.minSpeechDurationDescription')}</small>
                </div>

                <div className="form-group">
                  <label htmlFor="minSilenceDuration">{t('form.minSilenceDuration')}</label>
                  <input
                    type="number"
                    id="minSilenceDuration"
                    value={minSilenceDuration}
                    onChange={(e) => setMinSilenceDuration(parseInt(e.target.value) || 500)}
                    min="100"
                    max="5000"
                    step="100"
                    disabled={isProcessing}
                  />
                  <small>{t('form.minSilenceDurationDescription')}</small>
                </div>

                <h3>{t('form.asrConfig')}</h3>

                {/* Language selection - common for all ASR methods */}
                <div className="form-group">
                  <label htmlFor="asrLanguage">{t('asr.language')}</label>
                  <select
                    id="asrLanguage"
                    value={asrLanguage}
                    onChange={(e) => setAsrLanguage(e.target.value)}
                    disabled={isProcessing}
                  >
                    <option value="auto">{t('asr.autoDetect')}</option>
                    <option value="zh">{t('asr.chinese')}</option>
                    <option value="en">{t('asr.english')}</option>
                    <option value="ja">{t('asr.japanese')}</option>
                  </select>
                  <small>{t('asr.languageDescription')}</small>
                </div>

                {/* Faster Whisper configuration */}
                {asrMethod === 'faster-whisper' && (
                  <div className="asr-config-section">
                    <div className="form-group">
                      <label htmlFor="asrApiUrl">{t('asr.fasterWhisper.apiUrl')}</label>
                      <input
                        type="text"
                        id="asrApiUrl"
                        value={asrApiUrl}
                        onChange={(e) => setAsrApiUrl(e.target.value)}
                        placeholder="https://asr-ai.immiqnas.heiyu.space/v1/audio/transcriptions"
                        disabled={isProcessing}
                      />
                      <small>{t('asr.fasterWhisper.apiUrlDescription')}</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrApiKey">{t('asr.fasterWhisper.apiKey')}</label>
                      <input
                        type="password"
                        id="asrApiKey"
                        value={asrApiKey}
                        onChange={(e) => setAsrApiKey(e.target.value)}
                        placeholder="API Key"
                        disabled={isProcessing}
                      />
                      <small>{t('asr.fasterWhisper.apiKeyDescription')}</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrModel">{t('asr.fasterWhisper.model')}</label>
                      <input
                        type="text"
                        id="asrModel"
                        value={asrModel}
                        onChange={(e) => setAsrModel(e.target.value)}
                        placeholder="Systran/faster-whisper-large-v2"
                        disabled={isProcessing}
                      />
                      <small>{t('asr.fasterWhisper.modelDescription')}</small>
                    </div>
                  </div>
                )}

                {/* Qwen ASR configuration */}
                {asrMethod === 'qwen-asr' && (
                  <div className="asr-config-section">
                    <div className="form-group">
                      <label htmlFor="asrApiUrl">{t('asr.qwenASR.apiUrl')}</label>
                      <input
                        type="text"
                        id="asrApiUrl"
                        value="https://dashscope.aliyuncs.com/api/v1/services/aigc/audio/asr"
                        readOnly
                        disabled
                        className="readonly-input"
                      />
                      <small>{t('asr.qwenASR.apiUrlDescription')}</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrApiKey">{t('asr.qwenASR.apiKey')}</label>
                      <input
                        type="password"
                        id="asrApiKey"
                        value={asrApiKey}
                        onChange={(e) => setAsrApiKey(e.target.value)}
                        placeholder="Enter Alibaba Cloud API Key"
                        disabled={isProcessing}
                      />
                      <small>{t('asr.qwenASR.apiKeyDescription')}</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrModel">{t('asr.qwenASR.model')}</label>
                      <select
                        id="asrModel"
                        value={asrModel}
                        onChange={(e) => setAsrModel(e.target.value)}
                        disabled={isProcessing}
                      >
                        <option value="qwen3-asr-flash">qwen3-asr-flash</option>
                      </select>
                      <small>{t('asr.qwenASR.modelDescription')}</small>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="submit-buttons">
            <button
              type="button"
              onClick={handleSingleSubmit}
              className="process-button"
              disabled={isProcessing || audioFiles.length !== 1}
            >
              {isProcessing ? t('buttons.processing') : t('buttons.processSingle')}
            </button>

            <button
              type="button"
              onClick={handleMultipleSubmit}
              className="process-button multiple"
              disabled={isProcessing || audioFiles.length === 0}
            >
              {isProcessing ? t('buttons.batchProcessing') : `${t('buttons.processMultiple')} (${audioFiles.length})`}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {isProcessing && (
          <div className="processing-indicator">
            <p>{t('processing.processing')}</p>
          </div>
        )}

        {result && (
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
        )}

        {multiFileResult && (
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
        )}
      </main>
    </div>
  );
}

export default App;
