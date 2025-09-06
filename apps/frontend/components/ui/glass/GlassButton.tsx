import React from 'react';
import { cn } from '@/lib/utils';

interface GlassButtonProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'dark' | 'blue' | 'purple' | 'light';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  className = '',
  variant = 'default',
  size = 'md',
  onClick,
  disabled = false,
  type = 'button',
  icon,
  fullWidth = false,
}) => {
  const baseClasses = 'relative rounded-lg backdrop-blur-md border transition-all duration-300 inline-flex items-center justify-center';
  
  // Variant styles
  const variantClasses = {
    default: 'bg-glass border-glass hover:bg-glass-lighter text-white',
    dark: 'bg-glass-dark border-glass-dark hover:bg-glass-darker text-white',
    blue: 'bg-glass-blue border-glass-blue hover:bg-blue-600/20 text-blue-50',
    purple: 'bg-glass-purple border-glass-purple hover:bg-purple-600/20 text-purple-50',
    light: 'bg-glass-light border-glass-light hover:bg-glass-lighter text-gray-800',
  };

  // Size styles
  const sizeClasses = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-base px-4 py-2',
    lg: 'text-lg px-6 py-3',
  };

  // Disabled styles
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-glass-strong';

  // Full width
  const widthClasses = fullWidth ? 'w-full' : '';

  return (
    <button
      type={type}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        disabledClasses,
        widthClasses,
        className
      )}
      onClick={onClick}
      disabled={disabled}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
};

export default GlassButton;
