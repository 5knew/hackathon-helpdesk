import React from 'react';

interface BrandBarProps {
  subtitle?: string;
  rightContent?: React.ReactNode;
}

export const BrandBar: React.FC<BrandBarProps> = ({ subtitle = 'Единый вход и мониторинг', rightContent }) => {
  return (
    <header className="brand-bar">
      <div className="brand">
        <div className="logo-dot"></div>
        <div>
          <p className="brand-name">AI AutoResponder</p>
          <span className="brand-sub">{subtitle}</span>
        </div>
      </div>
      {rightContent}
    </header>
  );
};

