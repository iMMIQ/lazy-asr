import React from 'react';
import { useTranslation } from 'react-i18next';
import './TabNavigation.css';

/**
 * Tab Navigation Component
 * Provides navigation between different tabs (upload, scan, etc.)
 */
const TabNavigation = ({ activeTab, onTabChange, tabs = ['upload', 'scan'] }) => {
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
};

export default TabNavigation;
