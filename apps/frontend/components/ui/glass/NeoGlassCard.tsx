import React from 'react';
import { cn } from '@/lib/utils';

interface NeoGlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'frost' | 'smoke' | 'neo' | 'gradient' | 'dark';
  animation?: 'none' | 'pulse' | 'float' | 'refract' | 'color-shift';
  glare?: boolean;
  depth?: 'flat' | 'medium' | 'deep';
}

/**
 * Neo Glass Card - A modern 2025 implementation of glassmorphism 
 * with advanced visual effects and animations
 */
export const NeoGlassCard: React.FC<NeoGlassCardProps> = ({
  children,
  className = '',
  variant = 'frost',
  animation = 'none',
  glare = false,
  depth = 'medium',
}) => {
  // Base styles
  const baseClasses = "relative rounded-xl overflow-hidden backdrop-blur-md";
  
  // Variant styles
  const variantClasses = {
    frost: 'bg-glass-frost border border-white/20',
    smoke: 'bg-glass-smoke border border-white/10',
    neo: 'bg-glass-neo border border-white/20',
    gradient: 'bg-glass-gradient border border-white/10',
    dark: 'bg-glass-gradient-dark border border-white/5',
  };
  
  // Depth styles
  const depthClasses = {
    flat: 'shadow-glass',
    medium: 'shadow-glass-double',
    deep: 'shadow-glass-neo',
  };
  
  // Animation styles
  const animationClasses = {
    none: '',
    pulse: 'animate-pulse-glass',
    float: 'animate-float',
    refract: 'animate-refract',
    'color-shift': 'animate-color-shift',
  };
  
  // Generate additional class for the glare effect
  const glareElement = glare ? (
    <div className="absolute inset-0 pointer-events-none">
      <div className="absolute -inset-full bg-gradient-to-r from-transparent via-white/10 to-transparent transform rotate-45 translate-y-full animate-[shimmer_5s_linear_infinite]"></div>
      <div className="absolute top-0 left-1/2 w-3/4 h-1/2 bg-gradient-radial from-white/20 to-transparent opacity-50 blur-xl rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
    </div>
  ) : null;

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        depthClasses[depth],
        animationClasses[animation],
        className
      )}
    >
      {glare && glareElement}
      <div className="relative z-10">{children}</div>
    </div>
  );
};

export default NeoGlassCard;
