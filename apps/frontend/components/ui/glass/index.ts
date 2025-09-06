export { default as GlassCard } from './GlassCard';
export { default as GlassButton } from './GlassButton';
export { default as GlassInput } from './GlassInput';
export { default as GlassContainer } from './GlassContainer';
export { default as NeoGlassCard } from './NeoGlassCard';

// Add the shimmer animation keyframes
export const glassStyles = `
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes pulse-glass {
  0% { backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.1); }
  50% { backdrop-filter: blur(15px); background-color: rgba(255, 255, 255, 0.15); }
  100% { backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.1); }
}

@keyframes refract {
  0% { backdrop-filter: blur(10px) hue-rotate(0deg); }
  50% { backdrop-filter: blur(12px) hue-rotate(15deg); }
  100% { backdrop-filter: blur(10px) hue-rotate(0deg); }
}
`;
