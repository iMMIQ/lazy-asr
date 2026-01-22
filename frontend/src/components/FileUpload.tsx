import React from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, FileAudio, X } from 'lucide-react';

/** File upload component props */
export interface FileUploadProps {
  audioFiles: File[];
  onFilesChange: (files: File[]) => void;
  onFileRemove: (index: number) => void;
  isProcessing: boolean;
}

/**
 * File upload component with file list management
 */
export function FileUpload({
  audioFiles,
  onFilesChange,
  onFileRemove,
  isProcessing
}: FileUploadProps): React.ReactElement {
  const { t } = useTranslation();

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    onFilesChange(files);
  };

  const removeFile = (index: number) => {
    onFileRemove(index);
  };

  const handleDropzoneClick = () => {
    document.getElementById('mediaFile')?.click();
  };

  return (
    <div className="form-group">
      <label htmlFor="audioFile" className="file-upload-label">
        <Upload className="label-icon" size={20} />
        {t('form.uploadAudio')}
      </label>
      <div className="file-upload-container">
        <input
          type="file"
          id="mediaFile"
          accept="audio/*,video/*"
          multiple
          onChange={handleFileChange}
          disabled={isProcessing}
          className="file-input"
        />
        <div
          className="file-upload-dropzone"
          onClick={handleDropzoneClick}
          role="button"
          tabIndex={0}
        >
          <Upload className="upload-icon" size={48} strokeWidth={1.5} />
          <p className="upload-text">{t('form.uploadHint') || '点击或拖拽文件到此处'}</p>
          <p className="upload-subtext">支持音频和视频文件</p>
        </div>
      </div>
      <small className="max-files-hint">{t('form.maxFiles')}</small>

      {audioFiles.length > 0 && (
        <div className="file-list">
          <h4 className="file-list-header">
            <FileAudio size={18} className="list-icon" />
            {t('form.selectedFiles')} ({audioFiles.length})
          </h4>
          <ul>
            {audioFiles.map((file, index) => (
              <li key={index} className="file-item">
                <FileAudio size={16} className="file-icon" />
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{formatFileSize(file.size)}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  disabled={isProcessing}
                  className="remove-file-btn"
                  title={t('form.removeFile')}
                >
                  <X size={16} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
