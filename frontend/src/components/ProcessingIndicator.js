import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Processing indicator component to show loading state
 */
const ProcessingIndicator = ({ isProcessing, error }) => {
  const { t } = useTranslation();

  if (error) {
    return (
      <div className="error-message">
        ❌ {error}
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="processing-indicator">
        <p>{t('processing.processing')}</p>
      </div>
    );
  }

  return null;
};

export default ProcessingIndicator;
