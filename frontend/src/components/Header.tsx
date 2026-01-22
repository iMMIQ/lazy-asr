import React from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, Globe } from 'lucide-react';

/** Header component props */
export interface HeaderProps {
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
}

/**
 * Header component with title, description and language switcher
 */
export function Header({ currentLanguage, onLanguageChange }: HeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const changeLanguage = (lng: string) => {
    onLanguageChange(lng);
  };

  return (
    <header className="App-header">
      <div className="header-icon">
        <Mic size={48} strokeWidth={2} />
      </div>
      <h1>{t('app.title')}</h1>
      <p>{t('app.description')}</p>
      <div className="language-switcher">
        <Globe className="globe-icon" size={18} />
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
}

export default Header;
