import React from 'react';
import { cn } from '@/lib/utils';

interface GlassInputProps {
  className?: string;
  label?: string;
  name: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  error?: string;
  variant?: 'default' | 'dark' | 'blue' | 'purple' | 'light';
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export const GlassInput: React.FC<GlassInputProps> = ({
  className = '',
  label,
  name,
  placeholder,
  value,
  onChange,
  type = 'text',
  error,
  variant = 'default',
  disabled = false,
  fullWidth = false,
  icon,
}) => {
  const inputBaseClasses = 'rounded-lg backdrop-blur-md px-4 py-2.5 placeholder:text-gray-400 focus:outline-none focus:ring-2 transition-all duration-300';
  
  // Variant styles
  const variantClasses = {
    default: 'bg-glass border-glass text-white focus:ring-white/30',
    dark: 'bg-glass-dark border-glass-dark text-white focus:ring-white/30',
    blue: 'bg-glass-blue border-glass-blue text-blue-50 focus:ring-blue-300/30',
    purple: 'bg-glass-purple border-glass-purple text-purple-50 focus:ring-purple-300/30',
    light: 'bg-glass-light border-glass-light text-gray-800 focus:ring-gray-300/50',
  };

  // Error styles
  const errorClasses = error ? 'border-red-500/50 focus:ring-red-500/30' : `border-${variantClasses[variant].split(' ')[1]}`;
  
  // Width styles
  const widthClasses = fullWidth ? 'w-full' : '';
  
  // Disabled styles
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : '';

  return (
    <div className={cn('flex flex-col space-y-1.5', widthClasses, className)}>
      {label && (
        <label htmlFor={name} className="text-sm font-medium text-gray-200">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          id={name}
          name={name}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={cn(
            inputBaseClasses,
            variantClasses[variant],
            errorClasses,
            widthClasses,
            disabledClasses,
            icon && 'pl-10',
            'border'
          )}
        />
      </div>
      {error && <p className="text-red-400 text-xs">{error}</p>}
    </div>
  );
};

export default GlassInput;
