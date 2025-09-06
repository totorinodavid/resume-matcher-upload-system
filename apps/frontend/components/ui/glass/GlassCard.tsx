import React from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'dark' | 'blue' | 'purple' | 'light';
  intensity?: 'default' | 'strong' | 'subtle';
  border?: boolean;
  hoverEffect?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  variant = 'default',
  intensity = 'default',
  border = true,
  hoverEffect = false,
}) => {
  const baseClasses = 'relative rounded-xl backdrop-blur-md';

  // Variant styles
  const variantClasses = {
    default: 'bg-glass',
    dark: 'bg-glass-dark',
    blue: 'bg-glass-blue',
    purple: 'bg-glass-purple',
    light: 'bg-glass-light',
  };

  // Border styles
  const borderClasses = {
    default: border ? 'border border-glass' : '',
    dark: border ? 'border border-glass-dark' : '',
    blue: border ? 'border border-glass-blue' : '',
    purple: border ? 'border border-glass-purple' : '',
    light: border ? 'border border-glass-light' : '',
  };

  // Shadow intensity
  const shadowClasses = {
    default: 'shadow-glass',
    strong: 'shadow-glass-strong',
    subtle: 'shadow-sm',
  };

  // Hover effect
  const hoverClasses = hoverEffect
    ? 'transition-all duration-300 hover:shadow-glass-strong hover:scale-[1.01]'
    : '';

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        borderClasses[variant],
        shadowClasses[intensity],
        hoverClasses,
        className
      )}
    >
      {children}
    </div>
  );
};

export default GlassCard;
