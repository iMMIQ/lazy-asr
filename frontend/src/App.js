import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function App() {
  const [audioFile, setAudioFile] = useState(null);
  const [asrMethod, setAsrMethod] = useState('faster-whisper');
  const [availablePlugins, setAvailablePlugins] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [minSpeechDuration, setMinSpeechDuration] = useState(500);
  const [minSilenceDuration, setMinSilenceDuration] = useState(500);
  const [asrApiUrl, setAsrApiUrl] = useState('');
  const [asrApiKey, setAsrApiKey] = useState('');
  const [asrModel, setAsrModel] = useState('');

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
    setAudioFile(event.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleMethodChange = (event) => {
    setAsrMethod(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!audioFile) {
      setError('请选择音频文件');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      formData.append('asr_method', asrMethod);

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

  const handleDownload = (filePath) => {
    const downloadUrl = `${API_BASE_URL}/asr/download/${encodeURIComponent(filePath)}`;
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎵 Lazy ASR - 音频转录工具</h1>
        <p>轻松上传音频文件，自动生成字幕文件</p>
      </header>

      <main className="App-main">
        <form onSubmit={handleSubmit} className="processing-form">
          <div className="form-group">
            <label htmlFor="audioFile">上传音频文件:</label>
            <input
              type="file"
              id="audioFile"
              accept="audio/*"
              onChange={handleFileChange}
              disabled={isProcessing}
            />
          </div>

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

          <button
            type="submit"
            className="process-button"
            disabled={isProcessing || !audioFile}
          >
            {isProcessing ? '🚀 处理中...' : '🚀 开始处理'}
          </button>
        </form>

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

              {result.srt_file_path && (
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
      </main>
    </div>
  );
}

export default App;
