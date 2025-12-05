import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'ghost' | 'subtle';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default' }) => {
  const className = variant === 'default' ? 'badge' : `badge ${variant}`;
  return <div className={className}>{children}</div>;
};

