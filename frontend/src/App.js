import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchPlugins } from './services/api';
import { ConfigProvider, useConfig } from './context/ConfigContext';

// Import components
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import FileUploadTab from './components/FileUploadTab';
import PathScanner from './components/PathScanner';
import MonitorManager from './components/MonitorManager';

import './App.css';

/**
 * Main App Component
 * Provides the overall application structure and manages top-level state
 */
function App() {
  const { t, i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState('upload');

  // Language switcher function
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <ConfigProvider>
      <AppContent
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLanguageChange={changeLanguage}
      />
    </ConfigProvider>
  );
}

/**
 * AppContent Component
 * Contains the actual UI elements wrapped by ConfigProvider
 */
function AppContent({ activeTab, onTabChange, onLanguageChange }) {
  const { t, i18n } = useTranslation();
  const { actions } = useConfig();

  // Fetch available plugins and set default method
  useEffect(() => {
    const initializeConfig = async () => {
      try {
        const response = await fetchPlugins();
        const plugins = response.plugins;
        const defaultMethod = response.default_method;

        actions.setAvailablePlugins(plugins);

        // Set the default method from backend configuration
        if (defaultMethod && plugins.includes(defaultMethod)) {
          actions.setAsrMethod(defaultMethod);
        } else if (plugins.length > 0) {
          // Fallback to first plugin if default is not available
          actions.setAsrMethod(plugins[0]);
        }
      } catch (err) {
        console.error('Failed to fetch plugins:', err);
      }
    };

    initializeConfig();
  }, []);

  return (
    <div className="App">
      <Header
        currentLanguage={i18n.language}
        onLanguageChange={onLanguageChange}
      />

      <main className="App-main">
        {/* Tab Navigation */}
        <TabNavigation
          activeTab={activeTab}
          onTabChange={onTabChange}
          tabs={['upload', 'scan', 'monitor']}
        />

        {/* Tab Content */}
        {activeTab === 'upload' ? (
          <FileUploadTab />
        ) : activeTab === 'scan' ? (
          <PathScanner />
        ) : (
          <MonitorManager />
        )}
      </main>
    </div>
  );
}

export default App;
