import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function App() {
  const [audioFiles, setAudioFiles] = useState([]);
  const [asrMethod, setAsrMethod] = useState('faster-whisper');
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
  const [outputFormats, setOutputFormats] = useState(['srt']); // Default to SRT for backward compatibility

  // Fetch available plugins on component mount
  useEffect(() => {
    fetchAvailablePlugins();
  }, []);

  const fetchAvailablePlugins = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/asr/plugins`);
      setAvailablePlugins(response.data.plugins);
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
      setError('请选择单个音频文件');
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

      // 添加VAD参数
      if (showAdvancedOptions) {
        formData.append('min_speech_duration', minSpeechDuration);
        formData.append('min_silence_duration', minSilenceDuration);

        // 添加ASR配置参数
        if (asrApiUrl) formData.append('asr_api_url', asrApiUrl);
        if (asrApiKey) formData.append('asr_api_key', asrApiKey);
        if (asrModel) formData.append('asr_model', asrModel);
      }

      const response = await axios.post(`${API_BASE_URL}/asr/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      console.error('Processing failed:', err);
      setError(err.response?.data?.detail || '处理失败');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleMultipleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length === 0) {
      setError('请选择音频文件');
      return;
    }

    if (audioFiles.length > 10) {
      setError('一次最多处理10个文件');
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

      // 添加VAD参数
      if (showAdvancedOptions) {
        formData.append('min_speech_duration', minSpeechDuration);
        formData.append('min_silence_duration', minSilenceDuration);

        // 添加ASR配置参数
        if (asrApiUrl) formData.append('asr_api_url', asrApiUrl);
        if (asrApiKey) formData.append('asr_api_key', asrApiKey);
        if (asrModel) formData.append('asr_model', asrModel);
      }

      const response = await axios.post(`${API_BASE_URL}/asr/process-multiple`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMultiFileResult(response.data);
    } catch (err) {
      console.error('Batch processing failed:', err);
      setError(err.response?.data?.detail || '批量处理失败');
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

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎵 Lazy ASR - 音频转录工具</h1>
        <p>轻松上传音频文件，自动生成字幕文件</p>
      </header>

      <main className="App-main">
        <div className="processing-form">
          <div className="form-group">
            <label htmlFor="audioFile">上传音频文件:</label>
            <input
              type="file"
              id="audioFile"
              accept="audio/*"
              multiple
              onChange={handleFileChange}
              disabled={isProcessing}
            />
            <small>支持多文件上传，最多10个文件</small>
          </div>

          {audioFiles.length > 0 && (
            <div className="file-list">
              <h4>已选择的文件 ({audioFiles.length}个):</h4>
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
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="asrMethod">选择ASR服务:</label>
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
            <label>选择输出格式:</label>
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
            <small>选择要生成的字幕文件格式</small>
          </div>

          {/* 高级选项 */}
          <div className="advanced-options">
            <button
              type="button"
              className="advanced-toggle"
              onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            >
              {showAdvancedOptions ? '▼' : '▶'} 高级选项
            </button>

            {showAdvancedOptions && (
              <div className="advanced-content">
                <h3>VAD参数配置</h3>
                <div className="form-group">
                  <label htmlFor="minSpeechDuration">最小语音时长 (毫秒):</label>
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
                  <small>设置语音段的最小持续时间，较短的语音段将被忽略</small>
                </div>

                <div className="form-group">
                  <label htmlFor="minSilenceDuration">最小静音时长 (毫秒):</label>
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
                  <small>设置静音段的最小持续时间，用于分割语音段</small>
                </div>

                <h3>ASR服务配置</h3>

                {/* Faster Whisper 配置 */}
                {asrMethod === 'faster-whisper' && (
                  <div className="asr-config-section">
                    <div className="form-group">
                      <label htmlFor="asrApiUrl">API URL:</label>
                      <input
                        type="text"
                        id="asrApiUrl"
                        value={asrApiUrl}
                        onChange={(e) => setAsrApiUrl(e.target.value)}
                        placeholder="https://asr-ai.immiqnas.heiyu.space/v1/audio/transcriptions"
                        disabled={isProcessing}
                      />
                      <small>Faster Whisper API服务地址</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrApiKey">API Key (可选):</label>
                      <input
                        type="password"
                        id="asrApiKey"
                        value={asrApiKey}
                        onChange={(e) => setAsrApiKey(e.target.value)}
                        placeholder="API密钥"
                        disabled={isProcessing}
                      />
                      <small>如果API需要认证，请输入API密钥</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrModel">模型名称:</label>
                      <input
                        type="text"
                        id="asrModel"
                        value={asrModel}
                        onChange={(e) => setAsrModel(e.target.value)}
                        placeholder="Systran/faster-whisper-large-v2"
                        disabled={isProcessing}
                      />
                      <small>使用的语音识别模型</small>
                    </div>
                  </div>
                )}

                {/* Qwen ASR 配置 */}
                {asrMethod === 'qwen-asr' && (
                  <div className="asr-config-section">
                    <div className="form-group">
                      <label htmlFor="asrApiUrl">API URL:</label>
                      <input
                        type="text"
                        id="asrApiUrl"
                        value="https://dashscope.aliyuncs.com/api/v1/services/aigc/audio/asr"
                        readOnly
                        disabled
                        className="readonly-input"
                      />
                      <small>阿里云ASR服务地址 (固定)</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrApiKey">API Key:</label>
                      <input
                        type="password"
                        id="asrApiKey"
                        value={asrApiKey}
                        onChange={(e) => setAsrApiKey(e.target.value)}
                        placeholder="请输入阿里云API密钥"
                        disabled={isProcessing}
                      />
                      <small>阿里云DashScope API密钥</small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="asrModel">模型选择:</label>
                      <select
                        id="asrModel"
                        value={asrModel}
                        onChange={(e) => setAsrModel(e.target.value)}
                        disabled={isProcessing}
                      >
                        <option value="qwen3-asr-flash">qwen3-asr-flash</option>
                      </select>
                      <small>阿里云ASR模型 (目前仅支持qwen3-asr-flash)</small>
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
              {isProcessing ? '🚀 处理中...' : '🚀 处理单个文件'}
            </button>

            <button
              type="button"
              onClick={handleMultipleSubmit}
              className="process-button multiple"
              disabled={isProcessing || audioFiles.length === 0}
            >
              {isProcessing ? '🚀 批量处理中...' : `🚀 批量处理 (${audioFiles.length}个文件)`}
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
            <p>正在处理音频文件，请稍候...</p>
          </div>
        )}

        {result && (
          <div className="result-section">
            <h2>处理结果</h2>
            <div className="result-content">
              <p>{result.message}</p>

              {result.stats && (
                <div className="stats">
                  <h3>📊 统计信息:</h3>
                  <ul>
                    <li>总语音段数: {result.stats.total_segments}</li>
                    <li>成功转录段数: {result.stats.successful_transcriptions}</li>
                    <li>失败段数: {result.stats.failed_segments}</li>
                    <li>无内容段数: {result.stats.empty_segments}</li>
                    <li>总字幕数: {result.stats.total_subtitles}</li>
                  </ul>
                </div>
              )}

              {result.segments && result.segments.length > 0 && (
                <div className="segments-preview">
                  <h3>🎯 字幕预览:</h3>
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
                  <h3>📥 下载文件:</h3>
                  
                  {/* Bundle download button - show when multiple formats are selected */}
                  {Object.keys(result.output_files).length > 1 && result.task_id && (
                    <button
                      onClick={() => handleBundleDownload(result.task_id)}
                      className="download-button bundle-download-button"
                    >
                      📦 打包下载所有格式 ({Object.keys(result.output_files).length}个文件)
                    </button>
                  )}
                  
                  {/* Individual download buttons */}
                  {Object.entries(result.output_files).map(([format, filePath]) => (
                    <button
                      key={format}
                      onClick={() => handleDownload(filePath)}
                      className="download-button"
                    >
                      💾 下载{format.toUpperCase()}文件
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
                  💾 下载SRT文件
                </button>
              )}
            </div>
          </div>
        )}

        {multiFileResult && (
          <div className="result-section">
            <h2>批量处理结果</h2>
            <div className="result-content">
              <p>{multiFileResult.message}</p>

              {multiFileResult.overall_stats && (
                <div className="stats">
                  <h3>📊 总体统计信息:</h3>
                  <ul>
                    <li>总文件数: {multiFileResult.overall_stats.total_files}</li>
                    <li>成功处理文件数: {multiFileResult.overall_stats.successful_files}</li>
                    <li>失败文件数: {multiFileResult.overall_stats.failed_files}</li>
                    <li>总字幕数: {multiFileResult.overall_stats.total_subtitles}</li>
                    <li>总语音段数: {multiFileResult.overall_stats.total_segments}</li>
                  </ul>
                </div>
              )}

              <div className="file-results">
                <h3>📄 文件处理详情:</h3>
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
                            💾 {format.toUpperCase()}
                          </button>
                        ))}
                        {fileResult.task_id && (
                          <button
                            onClick={() => handleBundleDownload(fileResult.task_id)}
                            className="download-button small bundle"
                          >
                            📦 打包
                          </button>
                        )}
                      </div>
                    )}
                    
                    {fileResult.stats && (
                      <div className="file-stats">
                        <small>
                          字幕数: {fileResult.stats.total_subtitles} | 
                          语音段: {fileResult.stats.total_segments} | 
                          成功: {fileResult.stats.successful_transcriptions} | 
                          失败: {fileResult.stats.failed_segments}
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
