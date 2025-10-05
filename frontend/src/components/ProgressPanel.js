import React, { useState, useEffect, useRef } from 'react';
import './ProgressPanel.css';

const ProgressPanel = ({ taskId, isVisible, onClose }) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [currentMessage, setCurrentMessage] = useState('');
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  
  const wsRef = useRef(null);
  const logsEndRef = useRef(null);

  // Scroll to bottom of logs
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  // WebSocket connection management
  useEffect(() => {
    if (!taskId || !isVisible) {
      return;
    }

    const connectWebSocket = () => {
      try {
        const wsUrl = `ws://localhost:8000/api/v1/asr/ws/progress/${taskId}`;
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setConnectionError(null);
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        wsRef.current.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          setIsConnected(false);
          
          // If connection closed unexpectedly, show error
          if (event.code !== 1000) { // 1000 is normal closure
            setConnectionError(`Connection closed: ${event.reason || 'Unknown reason'}`);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionError('Failed to connect to progress server. Please check if the backend is running.');
          setIsConnected(false);
        };

      } catch (error) {
        console.error('Error creating WebSocket:', error);
        setConnectionError('Failed to establish WebSocket connection');
      }
    };

    connectWebSocket();

    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
      setIsConnected(false);
      setConnectionError(null);
    };
  }, [taskId, isVisible]);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'connection':
        console.log('WebSocket connection confirmed');
        break;

      case 'progress':
        setProgress(data.progress || 0);
        setCurrentStep(data.step || '');
        setCurrentMessage(data.message || '');
        
        if (data.details) {
          setStats(data.details);
        }
        
        // Add progress update to logs
        addLog('info', data.message, data.details);
        break;

      case 'log':
        addLog(data.level, data.message, data.details);
        break;

      case 'error':
        addLog('error', data.message, data.details);
        setConnectionError(data.message);
        break;

      case 'completion':
        addLog('success', 'Processing completed successfully!');
        setProgress(100);
        setCurrentStep('completion');
        setCurrentMessage('Processing completed successfully!');
        
        // Keep the connection open for a moment before closing
        setTimeout(() => {
          if (wsRef.current) {
            wsRef.current.close();
          }
        }, 2000);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const addLog = (level, message, details = null) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp,
      level,
      message,
      details
    };
    
    setLogs(prevLogs => [...prevLogs, logEntry].slice(-100)); // Keep last 100 logs
  };

  const getStepIcon = (step) => {
    const stepIcons = {
      initialization: '🚀',
      vad_detection: '🔍',
      segment_export: '📁',
      plugin_setup: '🔧',
      transcription: '🎯',
      srt_generation: '💾',
      completion: '✅'
    };
    return stepIcons[step] || '📝';
  };

  const getLogLevelClass = (level) => {
    const levelClasses = {
      info: 'log-info',
      success: 'log-success',
      warning: 'log-warning',
      error: 'log-error'
    };
    return levelClasses[level] || 'log-info';
  };

  const getLogLevelIcon = (level) => {
    const levelIcons = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    };
    return levelIcons[level] || 'ℹ️';
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="progress-panel">
      <div className="progress-panel-header">
        <h3>Real-time Progress</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      <div className="progress-panel-content">
        {/* Connection Status */}
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <div className="status-indicator"></div>
          <span>
            {isConnected ? 'Connected' : connectionError || 'Disconnected'}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-bar-container">
            <div 
              className="progress-bar" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">
            {Math.round(progress)}% - {currentMessage}
          </div>
        </div>

        {/* Current Step */}
        {currentStep && (
          <div className="current-step">
            <span className="step-icon">{getStepIcon(currentStep)}</span>
            <span className="step-text">{currentStep.replace('_', ' ').toUpperCase()}</span>
          </div>
        )}

        {/* Statistics */}
        {stats && (
          <div className="stats-section">
            <h4>Statistics</h4>
            <div className="stats-grid">
              {Object.entries(stats).map(([key, value]) => (
                <div key={key} className="stat-item">
                  <span className="stat-label">{key.replace(/_/g, ' ')}:</span>
                  <span className="stat-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logs */}
        <div className="logs-section">
          <h4>Processing Logs</h4>
          <div className="logs-container">
            {logs.length === 0 ? (
              <div className="no-logs">Waiting for logs...</div>
            ) : (
              logs.map(log => (
                <div key={log.id} className={`log-entry ${getLogLevelClass(log.level)}`}>
                  <span className="log-timestamp">{log.timestamp}</span>
                  <span className="log-level-icon">{getLogLevelIcon(log.level)}</span>
                  <span className="log-message">{log.message}</span>
                  {log.details && (
                    <div className="log-details">
                      {JSON.stringify(log.details, null, 2)}
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressPanel;
