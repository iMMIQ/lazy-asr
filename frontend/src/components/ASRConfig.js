import React from 'react';
import { useTranslation } from 'react-i18next';
import { OUTPUT_FORMATS } from '../constants/config';

/**
 * ASR configuration component with method selection and output format options
 */
const ASRConfig = ({
  asrMethod,
  availablePlugins,
  outputFormats,
  onMethodChange,
  onFormatChange,
  isProcessing
}) => {
  const { t } = useTranslation();

  const handleFormatChange = (format) => {
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
            <option key={plugin} value={plugin}>
              {plugin}
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
};

export default ASRConfig;
