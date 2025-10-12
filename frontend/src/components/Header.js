import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Header component with title, description and language switcher
 */
const Header = ({ currentLanguage, onLanguageChange }) => {
  const { t } = useTranslation();

  const changeLanguage = (lng) => {
    onLanguageChange(lng);
  };

  return (
    <header className="App-header">
      <h1>{t('app.title')}</h1>
      <p>{t('app.description')}</p>
      <div className="language-switcher">
        <button
          onClick={() => changeLanguage('zh')}
          className={currentLanguage === 'zh' ? 'active' : ''}
        >
          {t('language.chinese')}
        </button>
        <button
          onClick={() => changeLanguage('en')}
          className={currentLanguage === 'en' ? 'active' : ''}
        >
          {t('language.english')}
        </button>
      </div>
    </header>
  );
};

export default Header;
