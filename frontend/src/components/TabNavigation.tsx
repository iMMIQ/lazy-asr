import React from 'react';
import { useTranslation } from 'react-i18next';
import './TabNavigation.css';

/** Tab type for navigation - re-exported from types */
export type TabType = 'upload' | 'scanner';

/** Tab Navigation component props */
export interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  tabs?: TabType[];
}

/**
 * Tab Navigation Component
 * Provides navigation between different tabs (upload, scan, etc.)
 */
export function TabNavigation({
  activeTab,
  onTabChange,
  tabs = ['upload', 'scanner']
}: TabNavigationProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <div className="tab-navigation">
      <nav className="tab-nav">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
          >
            {t(`tabs.${tab}`)}
          </button>
        ))}
      </nav>
    </div>
  );
}

export default TabNavigation;
