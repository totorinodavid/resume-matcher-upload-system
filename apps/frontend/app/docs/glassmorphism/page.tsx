import React from 'react';
import { GlassCard, GlassButton, GlassInput, GlassContainer } from '@/components/ui/glass';

export default function GlassmorphismDocs() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-800 p-8">
      {/* Background decoration */}
      <div className="fixed -top-20 -left-20 w-96 h-96 rounded-full bg-blue-500/30 blur-3xl"></div>
      <div className="fixed top-1/3 -right-20 w-80 h-80 rounded-full bg-purple-500/30 blur-3xl"></div>
      <div className="fixed -bottom-20 left-1/3 w-72 h-72 rounded-full bg-indigo-500/30 blur-3xl"></div>
      
      <div className="max-w-4xl mx-auto relative z-10">
        <h1 className="text-4xl font-bold text-white text-center mb-8">Glassmorphism UI Components</h1>
        <p className="text-white/80 text-center mb-12 text-lg">A modern UI library for Resume Matcher featuring glassmorphic design elements.</p>
        
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Introduction</h2>
          <p className="text-white/80 mb-4">
            Glassmorphism is a modern UI design trend that creates a frosted glass effect using background blur, transparency, and subtle borders.
            This documentation showcases our custom glassmorphism components designed specifically for the Resume Matcher application.
          </p>
          <p className="text-white/80">
            These components are built with Tailwind CSS and React, ensuring full customizability and responsive behavior across all devices.
          </p>
        </GlassCard>
        
        {/* Glass Card Component */}
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">GlassCard</h2>
          <p className="text-white/80 mb-6">A versatile container component with glassmorphic styling. Supports various color variants and effects.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <GlassCard className="p-4" variant="default">
              <h3 className="text-white font-medium">Default</h3>
            </GlassCard>
            <GlassCard className="p-4" variant="dark">
              <h3 className="text-white font-medium">Dark</h3>
            </GlassCard>
            <GlassCard className="p-4" variant="blue">
              <h3 className="text-white font-medium">Blue</h3>
            </GlassCard>
            <GlassCard className="p-4" variant="purple">
              <h3 className="text-white font-medium">Purple</h3>
            </GlassCard>
          </div>
          
          <h3 className="text-xl font-bold text-white mb-4">Props</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-white/80">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="text-left py-2">Prop</th>
                  <th className="text-left py-2">Type</th>
                  <th className="text-left py-2">Default</th>
                  <th className="text-left py-2">Description</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">variant</td>
                  <td>string</td>
                  <td>'default'</td>
                  <td>Color variant: 'default', 'dark', 'blue', 'purple', 'light'</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">intensity</td>
                  <td>string</td>
                  <td>'default'</td>
                  <td>Shadow intensity: 'default', 'strong', 'subtle'</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">border</td>
                  <td>boolean</td>
                  <td>true</td>
                  <td>Whether to display a border</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">hoverEffect</td>
                  <td>boolean</td>
                  <td>false</td>
                  <td>Enables hover animation effect</td>
                </tr>
              </tbody>
            </table>
          </div>
        </GlassCard>
        
        {/* Glass Button Component */}
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">GlassButton</h2>
          <p className="text-white/80 mb-6">Interactive button with glassmorphic styling. Supports various colors, sizes, and states.</p>
          
          <div className="flex flex-wrap gap-4 mb-8">
            <GlassButton>Default</GlassButton>
            <GlassButton variant="dark">Dark</GlassButton>
            <GlassButton variant="blue">Blue</GlassButton>
            <GlassButton variant="purple">Purple</GlassButton>
            <GlassButton variant="light">Light</GlassButton>
          </div>
          
          <div className="flex flex-wrap gap-4 mb-8">
            <GlassButton size="sm">Small</GlassButton>
            <GlassButton size="md">Medium</GlassButton>
            <GlassButton size="lg">Large</GlassButton>
          </div>
          
          <div className="flex flex-wrap gap-4 mb-6">
            <GlassButton disabled>Disabled</GlassButton>
            <GlassButton fullWidth>Full Width</GlassButton>
          </div>
          
          <h3 className="text-xl font-bold text-white mb-4">Props</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-white/80">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="text-left py-2">Prop</th>
                  <th className="text-left py-2">Type</th>
                  <th className="text-left py-2">Default</th>
                  <th className="text-left py-2">Description</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">variant</td>
                  <td>string</td>
                  <td>'default'</td>
                  <td>Color variant: 'default', 'dark', 'blue', 'purple', 'light'</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">size</td>
                  <td>string</td>
                  <td>'md'</td>
                  <td>Button size: 'sm', 'md', 'lg'</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">disabled</td>
                  <td>boolean</td>
                  <td>false</td>
                  <td>Disables the button</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">fullWidth</td>
                  <td>boolean</td>
                  <td>false</td>
                  <td>Makes button take full width</td>
                </tr>
                <tr className="border-b border-white/10">
                  <td className="py-2 font-medium">icon</td>
                  <td>ReactNode</td>
                  <td>undefined</td>
                  <td>Optional icon element</td>
                </tr>
              </tbody>
            </table>
          </div>
        </GlassCard>
        
        {/* Glass Input Component */}
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">GlassInput</h2>
          <p className="text-white/80 mb-6">Input field with glassmorphic styling. Features label support, error handling, and various states.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <GlassInput 
              name="default-input" 
              label="Default Input" 
              placeholder="Enter text..." 
            />
            <GlassInput 
              name="blue-input" 
              label="Blue Variant" 
              placeholder="Search..." 
              variant="blue"
            />
            <GlassInput 
              name="error-input" 
              label="With Error" 
              placeholder="Email address" 
              error="Please enter a valid email"
            />
            <GlassInput 
              name="disabled-input" 
              label="Disabled Input" 
              placeholder="Cannot edit this" 
              disabled
            />
          </div>
        </GlassCard>
        
        {/* Glass Container Component */}
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">GlassContainer</h2>
          <p className="text-white/80 mb-6">A specialized container for creating larger glassmorphic sections with animation effects.</p>
          
          <GlassContainer className="p-6 mb-6" animated>
            <p className="text-white/90">This container has an animated shimmer effect.</p>
          </GlassContainer>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <GlassContainer className="p-4" intensity="light">
              <p className="text-white">Light blur</p>
            </GlassContainer>
            <GlassContainer className="p-4" intensity="medium">
              <p className="text-white">Medium blur</p>
            </GlassContainer>
            <GlassContainer className="p-4" intensity="strong">
              <p className="text-white">Strong blur</p>
            </GlassContainer>
          </div>
        </GlassCard>
        
        {/* Usage Guide */}
        <GlassCard className="p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Usage Guide</h2>
          <p className="text-white/80 mb-4">
            To use these components in your Resume Matcher application:
          </p>
          <div className="bg-gray-900/50 rounded-md p-4 mb-6">
            <pre className="text-blue-300 whitespace-pre-wrap">
              {`import { 
  GlassCard, 
  GlassButton, 
  GlassInput, 
  GlassContainer 
} from '@/components/ui/glass';`}
            </pre>
          </div>
          <p className="text-white/80 mb-4">
            For best results, place glassmorphic elements on a colorful background with a subtle gradient.
            Add decorative blurred shapes to enhance the glass effect.
          </p>
        </GlassCard>
        
        <GlassCard className="p-4 text-center mb-8">
          <p className="text-white/60">
            © 2025 Resume Matcher - Glassmorphism UI Documentation
          </p>
        </GlassCard>
      </div>
    </div>
  );
}
