import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language } from '../types';
import { getLanguage, setLanguage as setLang, t as translate } from '../utils/i18n';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(getLanguage());

  useEffect(() => {
    // Загружаем язык из localStorage при монтировании
    const savedLang = getLanguage();
    setLanguageState(savedLang);
    setLang(savedLang);
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    setLang(lang);
  };

  const t = (key: string): string => {
    // Используем актуальный язык из состояния
    return translate(key, language);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

