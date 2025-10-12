import React from 'react';
import { useTranslation } from 'react-i18next';
import { MAX_FILES } from '../constants/config';

/**
 * File upload component with file list management
 */
const FileUpload = ({ 
  audioFiles, 
  onFilesChange, 
  onFileRemove, 
  isProcessing 
}) => {
  const { t } = useTranslation();

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    onFilesChange(files);
  };

  const removeFile = (index) => {
    onFileRemove(index);
  };

  return (
    <div className="form-group">
      <label htmlFor="audioFile">{t('form.uploadAudio')}</label>
      <input
        type="file"
        id="mediaFile"
        accept="audio/*,video/*"
        multiple
        onChange={handleFileChange}
        disabled={isProcessing}
      />
      <small>{t('form.maxFiles')}</small>

      {audioFiles.length > 0 && (
        <div className="file-list">
          <h4>{t('form.selectedFiles')} ({audioFiles.length}):</h4>
          <ul>
            {audioFiles.map((file, index) => (
              <li key={index} className="file-item">
                <span>{file.name}</span>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  disabled={isProcessing}
                  className="remove-file-btn"
                >
                  {t('form.removeFile')}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
