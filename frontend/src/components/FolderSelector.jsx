import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { browseDirectory, getPathInfo } from '../services/api';

const FolderSelector = ({ onPathSelect, selectedPath, disabled = false }) => {
  const { t } = useTranslation();

  const [currentPath, setCurrentPath] = useState('/');
  const [directoryData, setDirectoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pathInfo, setPathInfo] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState(null);

  // Load initial directory data
  useEffect(() => {
    loadDirectory('/');
  }, []);

  // Load path info when selected folder changes
  useEffect(() => {
    if (selectedFolder) {
      loadPathInfo(selectedFolder);
    }
  }, [selectedFolder]);

  const loadDirectory = async (path) => {
    try {
      setLoading(true);
      setError(null);
      const data = await browseDirectory(path);
      setDirectoryData(data);
      setCurrentPath(data.current_path);
      setSelectedFolder(null);
      setPathInfo(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadPathInfo = async (path) => {
    try {
      setLoading(true);
      setError(null);
      const info = await getPathInfo(path);
      setPathInfo(info);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDirectoryClick = (path) => {
    loadDirectory(path);
  };

  const handleBreadcrumbClick = (path) => {
    loadDirectory(path);
  };

  const handleQuickAccess = (path) => {
    loadDirectory(path);
  };

  const handleSelectCurrentDirectory = () => {
    if (currentPath && onPathSelect) {
      onPathSelect(currentPath);
    }
  };

  const handleSelectFolder = () => {
    if (selectedFolder && onPathSelect) {
      onPathSelect(selectedFolder);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'audio':
        return '🎵';
      case 'video':
        return '🎬';
      default:
        return '📁';
    }
  };

  // Generate breadcrumb navigation
  const renderBreadcrumbs = () => {
    if (!currentPath) return null;

    const parts = currentPath.split('/').filter(Boolean);
    const breadcrumbs = [{ name: '🏠', path: '/' }];

    parts.forEach((part, index) => {
      const path = '/' + parts.slice(0, index + 1).join('/');
      breadcrumbs.push({ name: part, path });
    });

    return (
      <div className="breadcrumb-nav">
        {breadcrumbs.map((crumb, index) => (
          <React.Fragment key={index}>
            <button
              type="button"
              className={`breadcrumb-item ${index === breadcrumbs.length - 1 ? 'active' : ''}`}
              onClick={() => handleBreadcrumbClick(crumb.path)}
              disabled={disabled}
            >
              {index === 0 ? crumb.name : `📁 ${crumb.name}`}
            </button>
            {index < breadcrumbs.length - 1 && <span className="breadcrumb-separator">/</span>}
          </React.Fragment>
        ))}
      </div>
    );
  };

  return (
    <div className="folder-selector">
      <div className="folder-selector-header">
        <h3>{t('folderSelector.title')}</h3>
      </div>

      {/* Quick Access Buttons */}
      <div className="quick-access">
        <span className="quick-access-label">{t('folderSelector.quickAccess')}:</span>
        <button
          type="button"
          className="quick-access-btn"
          onClick={() => handleQuickAccess('/')}
          disabled={disabled}
        >
          {t('folderSelector.root')}
        </button>
        <button
          type="button"
          className="quick-access-btn"
          onClick={() => handleQuickAccess('~')}
          disabled={disabled}
        >
          {t('folderSelector.userDirectory')}
        </button>
        <button
          type="button"
          className="quick-access-btn"
          onClick={() => handleQuickAccess('/home')}
          disabled={disabled}
        >
          /home
        </button>
      </div>

      {/* Breadcrumb Navigation */}
      <div className="breadcrumb-container">
        {t('folderSelector.currentPath')}:
        {renderBreadcrumbs()}
      </div>

      {loading && !directoryData && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>{t('folderSelector.loading')}</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {directoryData && (
        <>
          {/* Directory List */}
          <div className="directory-list">
            {/* Parent Directory */}
            {directoryData.parent_path && (
              <button
                type="button"
                className="directory-item parent-dir"
                onClick={() => handleDirectoryClick(directoryData.parent_path)}
                disabled={disabled}
              >
                <span className="dir-icon">⬆️</span>
                <span className="dir-name">.. ({t('folderSelector.parentDirectory')})</span>
              </button>
            )}

            {/* Subdirectories */}
            {directoryData.directories && directoryData.directories.length > 0 ? (
              directoryData.directories.map((dir, index) => (
                <button
                  type="button"
                  key={index}
                  className="directory-item"
                  onClick={() => handleDirectoryClick(dir.path)}
                  disabled={disabled}
                >
                  <span className="dir-icon">📁</span>
                  <span className="dir-name">{dir.name}</span>
                </button>
              ))
            ) : (
              <div className="no-directories">
                {t('folderSelector.noDirectories')}
              </div>
            )}

            {/* Select Current Directory Button */}
            <button
              type="button"
              className="select-folder-btn"
              onClick={handleSelectCurrentDirectory}
              disabled={disabled}
              style={{ marginTop: '10px' }}
            >
              {t('folderSelector.selectThisFolder')} ({t('folderSelector.currentDirectory')})
            </button>
          </div>

          {/* Media Files in Current Directory */}
          {directoryData.media_files && directoryData.media_files.length > 0 && (
            <div className="media-files-preview">
              <h4>{t('folderSelector.mediaFiles')} ({t('folderSelector.currentDirectory')}):</h4>
              <div className="media-files-list">
                {directoryData.media_files.map((file, index) => (
                  <div key={index} className="media-file-item">
                    <span className="file-icon">{getIcon(file.type)}</span>
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{file.size}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Selected Folder Info */}
          {selectedFolder && pathInfo && (
            <div className="selected-folder-info">
              <h4>{t('folderSelector.selectedPath')}:</h4>
              <div className="selected-path-display">
                <code>{selectedFolder}</code>
              </div>
              <div className="path-stats">
                <div className="stat-item">
                  <span className="stat-label">{t('folderSelector.mediaCount')}:</span>
                  <span className="stat-value">{pathInfo.media_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">{t('folderSelector.totalSize')}:</span>
                  <span className="stat-value">{pathInfo.total_size} MB</span>
                </div>
              </div>
              {pathInfo.files && pathInfo.files.length > 0 && (
                <div className="selected-folder-files">
                  <h5>{t('folderSelector.filePreview')}:</h5>
                  <div className="media-files-list">
                    {pathInfo.files.map((file, index) => (
                      <div key={index} className="media-file-item">
                        <span className="file-icon">{getIcon(file.type)}</span>
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">{file.size} MB</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <button
                type="button"
                className="select-folder-btn"
                onClick={handleSelectFolder}
                disabled={disabled}
              >
                {t('folderSelector.selectThisFolder')}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FolderSelector;
