import React from 'react';
import { useConfig } from '../context/ConfigContext';
import useASRProcessing from '../hooks/useASRProcessing';
import FileUpload from './FileUpload';
import ConfigPanel from './ConfigPanel';
import SubmitButtons from './SubmitButtons';
import ProcessingIndicator from './ProcessingIndicator';
import ResultDisplay from './ResultDisplay';
import './FileUploadTab.css';

/**
 * File Upload Tab Component
 * Handles file upload, configuration, and ASR processing for individual files
 */
const FileUploadTab = () => {
  const { state, actions } = useConfig();
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

  const [audioFiles, setAudioFiles] = React.useState([]);

  const handleFileChange = (files) => {
    setAudioFiles(files);
    resetResults();
  };

  const handleFileRemove = (index) => {
    const newFiles = [...audioFiles];
    newFiles.splice(index, 1);
    setAudioFiles(newFiles);
  };

  const handleSingleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length !== 1) {
      return;
    }

    actions.setProcessing(true);

    try {
      const formData = buildFormData({
        audioFiles,
        asrMethod: state.asrMethod,
        outputFormats: state.outputFormats,
        outputMode: 'task',
        minSpeechDuration: state.minSpeechDuration,
        minSilenceDuration: state.minSilenceDuration,
        asrApiUrl: state.asrApiUrl,
        asrApiKey: state.asrApiKey,
        asrModel: state.asrModel,
        asrLanguage: state.asrLanguage,
        isMultiple: false
      });

      await processSingleFile(formData);
    } finally {
      actions.setProcessing(false);
    }
  };

  const handleMultipleSubmit = async (event) => {
    event.preventDefault();

    if (audioFiles.length === 0) {
      return;
    }

    actions.setProcessing(true);

    try {
      const formData = buildFormData({
        audioFiles,
        asrMethod: state.asrMethod,
        outputFormats: state.outputFormats,
        outputMode: 'task',
        minSpeechDuration: state.minSpeechDuration,
        minSilenceDuration: state.minSilenceDuration,
        asrApiUrl: state.asrApiUrl,
        asrApiKey: state.asrApiKey,
        asrModel: state.asrModel,
        asrLanguage: state.asrLanguage,
        isMultiple: true
      });

      await processMultipleFiles(formData);
    } finally {
      actions.setProcessing(false);
    }
  };

  return (
    <div className="file-upload-tab">
      <div className="processing-form">
        <FileUpload
          audioFiles={audioFiles}
          onFilesChange={handleFileChange}
          onFileRemove={handleFileRemove}
          isProcessing={isProcessing}
        />

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
                actions.setAsrLanguage(value);
                break;
              default:
                break;
            }
          }}
          showVadConfig={true}
          showAsrAdvancedConfig={true}
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
    </div>
  );
};

export default FileUploadTab;
