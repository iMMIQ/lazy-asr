import React from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2, AlertCircle } from 'lucide-react';

/** Processing indicator component props */
export interface ProcessingIndicatorProps {
  isProcessing: boolean;
  error?: string | null;
}

/**
 * Processing indicator component to show loading state
 */
export function ProcessingIndicator({ isProcessing, error }: ProcessingIndicatorProps): React.ReactElement | null {
  const { t } = useTranslation();

  if (error) {
    return (
      <div className="error-message">
        <AlertCircle size={24} />
        <span>{error}</span>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="processing-indicator">
        <Loader2 className="animate-spin" size={32} strokeWidth={2} />
        <p>{t('processing.processing')}</p>
      </div>
    );
  }

  return null;
}

export default ProcessingIndicator;
