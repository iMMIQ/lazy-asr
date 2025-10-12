import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchPlugins } from './services/api';
import useASRProcessing from './hooks/useASRProcessing';
import { 
  DEFAULT_OUTPUT_FORMATS,
  DEFAULT_MIN_SPEECH_DURATION,
  DEFAULT_MIN_SILENCE_DURATION
} from './constants/config';

// Import components
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ASRConfig from './components/ASRConfig';
import AdvancedOptions from './components/AdvancedOptions';
import SubmitButtons from './components/SubmitButtons';
import ProcessingIndicator from './components/ProcessingIndicator';
import ResultDisplay from './components/ResultDisplay';

import './App.css';

function App() {
  const { t, i18n } = useTranslation();
  
  // State management
  const [audioFiles, setAudioFiles] = useState([]);
  const [asrMethod, setAsrMethod] = useState('');
  const [availablePlugins, setAvailablePlugins] = useState([]);
  const [outputFormats, setOutputFormats] = useState(DEFAULT_OUTPUT_FORMATS);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [minSpeechDuration, setMinSpeechDuration] = useState(DEFAULT_MIN_SPEECH_DURATION);
  const [minSilenceDuration, setMinSilenceDuration] = useState(DEFAULT_MIN_SILENCE_DURATION);
  const [asrApiUrl, setAsrApiUrl] = useState('');
  const [asrApiKey, setAsrApiKey] = useState('');
  const [asrModel, setAsrModel] = useState('');
  const [asrLanguage, setAsrLanguage] = useState('auto');

  // Custom hook for processing logic
  const {
    isProcessing,
    error,
    result,
    multiFileResult,
    resetResults,
    handleSingleSubmit: processSingleFile,
    handleMultipleSubmit: processMultipleFiles,
    buildFormData
  } = useASRProcessing();

  // Fetch available plugins on component mount
  useEffect(() => {
    fetchAvailablePlugins();
  }, []);

  const fetchAvailablePlugins = async () => {
    try {
      const response = await fetchPlugins();
      const plugins = response.plugins;
      const defaultMethod = response.default_method;
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
    }
  };

  // Event handlers
  const handleFileChange = (files) => {
    setAudioFiles(files);
    resetResults();
  };

  const handleFileRemove = (index) => {
    const newFiles = [...audioFiles];
    newFiles.splice(index, 1);
    setAudioFiles(newFiles);
  };

  const handleMethodChange = (event) => {
    setAsrMethod(event.target.value);
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

  const handleVadConfigChange = (field, value) => {
    if (field === 'minSpeechDuration') {
      setMinSpeechDuration(value);
    } else if (field === 'minSilenceDuration') {
      setMinSilenceDuration(value);
    }
  };

  const handleAsrConfigChange = (field, value) => {
    switch (field) {
      case 'asrApiUrl':
        setAsrApiUrl(value);
        break;
      case 'asrApiKey':
        setAsrApiKey(value);
        break;
      case 'asrModel':
        setAsrModel(value);
        break;
      case 'asrLanguage':
        setAsrLanguage(value);
        break;
      default:
        break;
    }
  };

  const handleSingleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length !== 1) {
      return;
    }

    const formData = buildFormData({
      audioFiles,
      asrMethod,
      outputFormats,
      showAdvancedOptions,
      minSpeechDuration,
      minSilenceDuration,
      asrApiUrl,
      asrApiKey,
      asrModel,
      asrLanguage,
      isMultiple: false
    });

    await processSingleFile(formData);
  };

  const handleMultipleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length === 0) {
      return;
    }

    const formData = buildFormData({
      audioFiles,
      asrMethod,
      outputFormats,
      showAdvancedOptions,
      minSpeechDuration,
      minSilenceDuration,
      asrApiUrl,
      asrApiKey,
      asrModel,
      asrLanguage,
      isMultiple: true
    });

    await processMultipleFiles(formData);
  };

  // Language switcher function
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="App">
      <Header 
        currentLanguage={i18n.language} 
        onLanguageChange={changeLanguage} 
      />

      <main className="App-main">
        <div className="processing-form">
          <FileUpload
            audioFiles={audioFiles}
            onFilesChange={handleFileChange}
            onFileRemove={handleFileRemove}
            isProcessing={isProcessing}
          />

          <ASRConfig
            asrMethod={asrMethod}
            availablePlugins={availablePlugins}
            outputFormats={outputFormats}
            onMethodChange={handleMethodChange}
            onFormatChange={handleFormatChange}
            isProcessing={isProcessing}
          />

          <AdvancedOptions
            showAdvancedOptions={showAdvancedOptions}
            onToggleAdvancedOptions={() => setShowAdvancedOptions(!showAdvancedOptions)}
            minSpeechDuration={minSpeechDuration}
            minSilenceDuration={minSilenceDuration}
            asrLanguage={asrLanguage}
            asrApiUrl={asrApiUrl}
            asrApiKey={asrApiKey}
            asrModel={asrModel}
            asrMethod={asrMethod}
            onVadConfigChange={handleVadConfigChange}
            onAsrConfigChange={handleAsrConfigChange}
            isProcessing={isProcessing}
          />

          <SubmitButtons
            audioFiles={audioFiles}
            isProcessing={isProcessing}
            onSingleSubmit={handleSingleSubmit}
            onMultipleSubmit={handleMultipleSubmit}
          />
        </div>

        <ProcessingIndicator
          isProcessing={isProcessing}
          error={error}
        />

        <ResultDisplay
          result={result}
          multiFileResult={multiFileResult}
        />
      </main>
    </div>
  );
}

export default App;
