import React from 'react';
import { useTranslation } from 'react-i18next';
import { OUTPUT_FORMATS } from '../constants/config';
import type { OutputFormat, ASRPlugin } from '../types';

/** ASR configuration component props */
export interface ASRConfigProps {
  asrMethod: string;
  availablePlugins: ASRPlugin[];
  outputFormats: OutputFormat[];
  onMethodChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onFormatChange: (format: OutputFormat) => void;
  isProcessing: boolean;
}

/**
 * ASR configuration component with method selection and output format options
 */
export function ASRConfig({
  asrMethod,
  availablePlugins,
  outputFormats,
  onMethodChange,
  onFormatChange,
  isProcessing
}: ASRConfigProps): React.ReactElement {
  const { t } = useTranslation();

  const handleFormatChange = (format: OutputFormat) => {
    onFormatChange(format);
  };

  return (
    <>
      <div className="form-group">
        <label htmlFor="asrMethod">{t('form.selectASR')}</label>
        <select
          id="asrMethod"
          value={asrMethod}
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
                onChange={() => handleFormatChange(format)}
                disabled={isProcessing}
              />
              <span className="format-label">{format.toUpperCase()}</span>
            </label>
          ))}
        </div>
        <small>{t('form.outputFormatsDescription')}</small>
      </div>
    </>
  );
}

export default ASRConfig;
