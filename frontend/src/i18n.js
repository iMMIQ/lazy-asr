import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import zhTranslation from './locales/zh.json';
import enTranslation from './locales/en.json';

// Configure i18n
i18n
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    resources: {
      zh: {
        translation: zhTranslation
      },
      en: {
        translation: enTranslation
      }
    },
    fallbackLng: 'zh', // Use Chinese as fallback language
    debug: process.env.NODE_ENV === 'development', // Enable debug mode in development
    interpolation: {
      escapeValue: false, // React already safes from xss
    },
    detection: {
      order: ['localStorage', 'navigator'], // Check localStorage first, then browser language
      caches: ['localStorage'], // Cache language in localStorage
    },
  });

export default i18n;
