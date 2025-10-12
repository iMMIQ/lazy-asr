import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Submit buttons component for single and multiple file processing
 */
const SubmitButtons = ({
  audioFiles,
  isProcessing,
  onSingleSubmit,
  onMultipleSubmit
}) => {
  const { t } = useTranslation();

  return (
    <div className="submit-buttons">
      <button
        type="button"
        onClick={onSingleSubmit}
        className="process-button"
        disabled={isProcessing || audioFiles.length !== 1}
      >
        {isProcessing ? t('buttons.processing') : t('buttons.processSingle')}
      </button>

      <button
        type="button"
        onClick={onMultipleSubmit}
        className="process-button multiple"
        disabled={isProcessing || audioFiles.length === 0}
      >
        {isProcessing ? t('buttons.batchProcessing') : `${t('buttons.processMultiple')} (${audioFiles.length})`}
      </button>
    </div>
  );
};

export default SubmitButtons;
