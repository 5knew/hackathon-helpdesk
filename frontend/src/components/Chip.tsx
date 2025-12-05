import React from 'react';

interface ChipProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'ghost';
}

export const Chip: React.FC<ChipProps> = ({ children, variant = 'default' }) => {
  const className = variant === 'default' ? 'chip' : `chip ${variant}`;
  return <span className={className}>{children}</span>;
};

