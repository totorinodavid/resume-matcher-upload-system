import React from 'react';
import { cn } from '@/lib/utils';

interface GlassContainerProps {
  children: React.ReactNode;
  className?: string;
  intensity?: 'light' | 'medium' | 'strong';
  animated?: boolean;
  fullScreen?: boolean;
}

export const GlassContainer: React.FC<GlassContainerProps> = ({
  children,
  className = '',
  intensity = 'medium',
  animated = false,
  fullScreen = false,
}) => {
  // Base styling
  const baseClasses = 'relative overflow-hidden rounded-xl';
  
  // Backdrop blur intensity
  const blurClasses = {
    light: 'backdrop-blur-sm',
    medium: 'backdrop-blur-md',
    strong: 'backdrop-blur-lg',
  };
  
  // Animation classes
  const animationClasses = animated
    ? 'before:content-[""] before:absolute before:-inset-[100%] before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent before:transition-all before:duration-1000 before:animate-[shimmer_5s_infinite] before:translate-x-[-100%]'
    : '';
    
  // Fullscreen classes
  const fullScreenClasses = fullScreen
    ? 'fixed inset-0 z-10'
    : '';

  return (
    <div className={cn(
      baseClasses, 
      blurClasses[intensity], 
      animationClasses,
      fullScreenClasses,
      className
    )}>
      <div className="relative z-1">{children}</div>
    </div>
  );
};

// Add keyframes for shimmer animation to global CSS or use it with Tailwind config
// @keyframes shimmer {
//   0% { transform: translateX(-100%); }
//   100% { transform: translateX(100%); }
// }

export default GlassContainer;
