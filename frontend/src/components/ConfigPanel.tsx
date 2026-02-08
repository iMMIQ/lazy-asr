import React from 'react';
import { useTranslation } from 'react-i18next';
import { OUTPUT_FORMATS, LANGUAGE_OPTIONS, ASR_METHOD_CONFIGS } from '../constants/config';
import type { OutputFormat, LanguageCode, ASRFieldConfig, ASRMethodConfig, ASRPlugin } from '../types';

/** Config panel event handlers */
export interface ConfigPanelHandlers {
  onMethodChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onFormatChange?: (format: OutputFormat) => void;
  onVadConfigChange?: (field: string, value: number) => void;
  onAsrConfigChange?: (field: string, value: string) => void;
  onMaxFilesChange?: (value: number) => void;
  onRecursiveChange?: (checked: boolean) => void;
}

/** Config panel component props */
export interface ConfigPanelProps {
  // Configuration values
  asrMethod: string;
  availablePlugins: ASRPlugin[];
  outputFormats?: OutputFormat[];
  minSpeechDuration?: number;
  minSilenceDuration?: number;
  asrLanguage?: LanguageCode;
  asrApiUrl?: string;
  asrApiKey?: string;
  asrModel?: string;

  // Event handlers
  onMethodChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onFormatChange?: (format: OutputFormat) => void;
  onVadConfigChange?: (field: string, value: number) => void;
  onAsrConfigChange?: (field: string, value: string) => void;

  // Control options
  showVadConfig?: boolean;
  showAsrAdvancedConfig?: boolean;
  isProcessing?: boolean;

  // Additional options
  showMaxFiles?: boolean;
  maxFiles?: number;
  onMaxFilesChange?: (value: number) => void;

  showRecursiveOption?: boolean;
  recursive?: boolean;
  onRecursiveChange?: (checked: boolean) => void;
}

/**
 * Unified configuration panel for ASR/VAD settings
 * Reusable across file upload and path scanning components
 */
export function ConfigPanel({
  // Configuration values
  asrMethod,
  availablePlugins,
  outputFormats = [],
  minSpeechDuration = 500,
  minSilenceDuration = 500,
  asrLanguage = 'auto',
  asrApiUrl = '',
  asrApiKey = '',
  asrModel = '',

  // Event handlers
  onMethodChange,
  onFormatChange,
  onVadConfigChange,
  onAsrConfigChange,

  // Control options
  showVadConfig = true,
  showAsrAdvancedConfig = true,
  isProcessing = false,

  // Additional options
  showMaxFiles = false,
  maxFiles = 100,
  onMaxFilesChange,

  showRecursiveOption = false,
  recursive = false,
  onRecursiveChange
}: ConfigPanelProps): React.ReactElement {
  const { t } = useTranslation();

  const handleVadChange = (field: 'minSpeechDuration' | 'minSilenceDuration', value: string) => {
    if (onVadConfigChange) {
      onVadConfigChange(field, parseInt(value) || 500);
    }
  };

  const handleAsrConfigChange = (field: string, value: string) => {
    if (onAsrConfigChange) {
      onAsrConfigChange(field, value);
    }
  };

  const getAsrConfig = (): ASRMethodConfig => {
    return ASR_METHOD_CONFIGS[asrMethod] || {};
  };

  const renderAsrAdvancedConfig = () => {
    const config = getAsrConfig();

    if (!config || Object.keys(config).length === 0 || !showAsrAdvancedConfig) {
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
              value={config.apiUrl.value || asrApiUrl || ''}
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
              value={asrApiKey || ''}
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
                value={asrModel || ''}
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
                value={asrModel || ''}
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
    <div className="config-panel">
      {/* ASR Method Selection */}
      <div className="form-group">
        <label htmlFor="asrMethod">{t('form.selectASR')}</label>
        <select
          id="asrMethod"
          value={asrMethod || ''}
          onChange={onMethodChange}
          disabled={isProcessing}
        >
          {availablePlugins.map((plugin) => (
            <option key={plugin.name} value={plugin.name}>
              {plugin.display_name}
            </option>
          ))}
        </select>
      </div>

      {/* Output Format Selection */}
      <div className="form-group">
        <label>{t('form.selectOutputFormats')}</label>
        <div className="format-checkboxes">
          {OUTPUT_FORMATS.map((format) => (
            <label
              key={format}
              className={`format-checkbox ${outputFormats.includes(format) ? 'selected' : ''}`}
            >
              <input
                type="checkbox"
                checked={outputFormats.includes(format)}
                onChange={() => onFormatChange && onFormatChange(format)}
                disabled={isProcessing}
              />
              <span className="format-label">{format.toUpperCase()}</span>
            </label>
          ))}
        </div>
        <small>{t('form.outputFormatsDescription')}</small>
      </div>

      {/* Language Selection */}
      <div className="form-group">
        <label htmlFor="asrLanguage">{t('asr.language')}</label>
        <select
          id="asrLanguage"
          value={asrLanguage || 'auto'}
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

      {/* VAD Configuration */}
      {showVadConfig && (
        <>
          <h3>{t('form.vadConfig')}</h3>
          <div className="form-group">
            <label htmlFor="minSpeechDuration">{t('form.minSpeechDuration')}</label>
            <input
              type="number"
              id="minSpeechDuration"
              value={minSpeechDuration || 500}
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
              value={minSilenceDuration || 500}
              onChange={(e) => handleVadChange('minSilenceDuration', e.target.value)}
              min="100"
              max="5000"
              step="100"
              disabled={isProcessing}
            />
            <small>{t('form.minSilenceDurationDescription')}</small>
          </div>
        </>
      )}

      {/* ASR Advanced Configuration */}
      {showAsrAdvancedConfig && (
        <>
          <h3>{t('form.asrConfig')}</h3>
          {renderAsrAdvancedConfig()}
        </>
      )}

      {/* Optional: Max Files (for path scanning) */}
      {showMaxFiles && (
        <div className="form-group">
          <label htmlFor="maxFiles">{t('pathScanner.maxFiles')}</label>
          <input
            type="number"
            id="maxFiles"
            value={maxFiles || 100}
            onChange={(e) => onMaxFilesChange && onMaxFilesChange(parseInt(e.target.value) || 100)}
            min="1"
            max="1000"
            disabled={isProcessing}
          />
        </div>
      )}

      {/* Optional: Recursive Scan Option */}
      {showRecursiveOption && (
        <div className="form-group">
          <div className="recursive-checkbox">
            <input
              type="checkbox"
              id="recursive-scan"
              checked={recursive || false}
              onChange={(e) => onRecursiveChange && onRecursiveChange(e.target.checked)}
              disabled={isProcessing}
            />
            <label htmlFor="recursive-scan">
              {t('pathScanner.recursiveScan')}
            </label>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConfigPanel;
