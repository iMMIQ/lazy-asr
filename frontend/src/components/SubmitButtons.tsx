import React from 'react';
import { useTranslation } from 'react-i18next';
import { Play, Layers, Loader2 } from 'lucide-react';

/** Submit buttons component props */
export interface SubmitButtonsProps {
  audioFiles: File[];
  isProcessing: boolean;
  onSingleSubmit: (e?: React.FormEvent) => void | Promise<void>;
  onMultipleSubmit: (e?: React.FormEvent) => void | Promise<void>;
}

/**
 * Submit buttons component for single and multiple file processing
 */
export function SubmitButtons({
  audioFiles,
  isProcessing,
  onSingleSubmit,
  onMultipleSubmit
}: SubmitButtonsProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <div className="submit-buttons">
      <button
        type="button"
        onClick={onSingleSubmit}
        className="process-button"
        disabled={isProcessing || audioFiles.length !== 1}
      >
        {isProcessing ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            {t('buttons.processing')}
          </>
        ) : (
          <>
            <Play size={20} strokeWidth={2.5} />
            {t('buttons.processSingle')}
          </>
        )}
      </button>

      <button
        type="button"
        onClick={onMultipleSubmit}
        className="process-button multiple"
        disabled={isProcessing || audioFiles.length === 0}
      >
        {isProcessing ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            {t('buttons.batchProcessing')}
          </>
        ) : (
          <>
            <Layers size={20} strokeWidth={2} />
            {`${t('buttons.processMultiple')} (${audioFiles.length})`}
          </>
        )}
      </button>
    </div>
  );
}

export default SubmitButtons;
