import React from 'react';
import { useTranslation } from 'react-i18next';
import { 
  DEFAULT_MIN_SPEECH_DURATION, 
  DEFAULT_MIN_SILENCE_DURATION,
  LANGUAGE_OPTIONS,
  ASR_METHOD_CONFIGS 
} from '../constants/config';

/**
 * Advanced options component with VAD and ASR-specific configurations
 */
const AdvancedOptions = ({
  showAdvancedOptions,
  onToggleAdvancedOptions,
  minSpeechDuration,
  minSilenceDuration,
  asrLanguage,
  asrApiUrl,
  asrApiKey,
  asrModel,
  asrMethod,
  onVadConfigChange,
  onAsrConfigChange,
  isProcessing
}) => {
  const { t } = useTranslation();

  const handleVadChange = (field, value) => {
    onVadConfigChange(field, parseInt(value) || (field === 'minSpeechDuration' ? DEFAULT_MIN_SPEECH_DURATION : DEFAULT_MIN_SILENCE_DURATION));
  };

  const handleAsrConfigChange = (field, value) => {
    onAsrConfigChange(field, value);
  };

  const getAsrConfig = () => {
    return ASR_METHOD_CONFIGS[asrMethod] || {};
  };

  const renderAsrConfigSection = () => {
    const config = getAsrConfig();
    
    if (!config || Object.keys(config).length === 0) {
      return null;
    }

    return (
      <div className="asr-config-section">
        {config.apiUrl && (
          <div className="form-group">
            <label htmlFor="asrApiUrl">{t(`asr.${asrMethod}.apiUrl`)}</label>
            <input
              type="text"
              id="asrApiUrl"
              value={config.apiUrl.value || asrApiUrl}
              onChange={(e) => handleAsrConfigChange('asrApiUrl', e.target.value)}
              placeholder={config.apiUrl.placeholder}
              readOnly={config.apiUrl.readOnly}
              disabled={isProcessing || config.apiUrl.readOnly}
              className={config.apiUrl.readOnly ? 'readonly-input' : ''}
            />
            <small>{t(`asr.${asrMethod}.apiUrlDescription`)}</small>
          </div>
        )}

        {config.apiKey && (
          <div className="form-group">
            <label htmlFor="asrApiKey">{t(`asr.${asrMethod}.apiKey`)}</label>
            <input
              type="password"
              id="asrApiKey"
              value={asrApiKey}
              onChange={(e) => handleAsrConfigChange('asrApiKey', e.target.value)}
              placeholder={config.apiKey.placeholder}
              disabled={isProcessing}
            />
            <small>{t(`asr.${asrMethod}.apiKeyDescription`)}</small>
          </div>
        )}

        {config.model && (
          <div className="form-group">
            <label htmlFor="asrModel">{t(`asr.${asrMethod}.model`)}</label>
            {config.model.options ? (
              <select
                id="asrModel"
                value={asrModel}
                onChange={(e) => handleAsrConfigChange('asrModel', e.target.value)}
                disabled={isProcessing}
              >
                {config.model.options.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                id="asrModel"
                value={asrModel}
                onChange={(e) => handleAsrConfigChange('asrModel', e.target.value)}
                placeholder={config.model.placeholder}
                disabled={isProcessing}
              />
            )}
            <small>{t(`asr.${asrMethod}.modelDescription`)}</small>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="advanced-options">
      <button
        type="button"
        className="advanced-toggle"
        onClick={onToggleAdvancedOptions}
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
              onChange={(e) => handleVadChange('minSpeechDuration', e.target.value)}
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
              onChange={(e) => handleVadChange('minSilenceDuration', e.target.value)}
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
              onChange={(e) => handleAsrConfigChange('asrLanguage', e.target.value)}
              disabled={isProcessing}
            >
              {LANGUAGE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {t(`asr.${option.value === 'auto' ? 'autoDetect' : option.value === 'zh' ? 'chinese' : option.value === 'en' ? 'english' : 'japanese'}`)}
                </option>
              ))}
            </select>
            <small>{t('asr.languageDescription')}</small>
          </div>

          {/* ASR method specific configuration */}
          {renderAsrConfigSection()}
        </div>
      )}
    </div>
  );
};

export default AdvancedOptions;
