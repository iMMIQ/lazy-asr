import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchPlugins, fetchVADProviders } from './services/api';
import { ConfigProvider, useConfig } from './context/ConfigContext';
import type { TabType } from './types';

// Import components
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import FileUploadTab from './components/FileUploadTab';
import PathScanner from './components/PathScanner';
import MonitorManager from './components/MonitorManager';

import './App.css';

/** AppContent component props */
interface AppContentProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  onLanguageChange: (language: string) => void;
}

/**
 * Main App Component
 * Provides the overall application structure and manages top-level state
 */
function App(): React.ReactElement {
  const { i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState<TabType>('upload');

  // Language switcher function
  const changeLanguage = (lng: string) => {
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
function AppContent({ activeTab, onTabChange, onLanguageChange }: AppContentProps): React.ReactElement {
  const { i18n } = useTranslation();
  const { actions, state } = useConfig();

  // Fetch available plugins and set default method
  useEffect(() => {
    const initializeConfig = async () => {
      try {
        const response = await fetchPlugins();
        const plugins = response.plugins;
        const defaultMethod = (response as { default_method?: string }).default_method;

        actions.setAvailablePlugins(plugins);

        // Set the default method from backend configuration
        if (defaultMethod && plugins.some(p => p.name === defaultMethod)) {
          actions.setAsrMethod(defaultMethod);
        } else if (plugins.length > 0) {
          // Fallback to first plugin if default is not available
          actions.setAsrMethod(plugins[0].name);
        }
      } catch (err) {
        console.error('Failed to fetch plugins:', err);
      }
    };

    initializeConfig();
  }, []);

  // Fetch VAD providers on mount
  useEffect(() => {
    const loadVADProviders = async () => {
      try {
        const response = await fetchVADProviders();
        actions.setAvailableVADProviders(response.providers);
        // Set default VAD method from backend
        if (response.default && !state.vadMethod) {
          actions.setVadMethod(response.default);
        }
      } catch (error) {
        console.error('Failed to load VAD providers:', error);
      }
    };
    loadVADProviders();
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
          tabs={['upload', 'scanner', 'monitor']}
        />

        {/* Tab Content */}
        {activeTab === 'upload' ? (
          <FileUploadTab />
        ) : activeTab === 'scanner' ? (
          <PathScanner />
        ) : (
          <MonitorManager />
        )}
      </main>
    </div>
  );
}

export default App;
