import React from 'react';
import { GlassButton, NeoGlassCard } from '@/components/ui/glass';

export default function ModernGlassmorphismDemo() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-800 p-8">
      {/* Moderne Hintergrundformen */}
      <div className="fixed top-20 left-20 w-96 h-96 rounded-full bg-gradient-radial from-blue-500/30 to-transparent blur-3xl"></div>
      <div className="fixed bottom-20 right-20 w-96 h-96 rounded-full bg-gradient-radial from-purple-500/30 to-transparent blur-3xl"></div>
      <div className="fixed top-1/2 left-1/2 w-96 h-96 rounded-full bg-gradient-radial from-indigo-500/30 to-transparent blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
      
      {/* Netzartiger Hintergrund für mehr Tiefe */}
      <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center opacity-10"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <h1 className="text-5xl font-bold text-white text-center mb-12">Modern Glassmorphism 2025</h1>
        <p className="text-white/70 text-center text-xl mb-16 max-w-3xl mx-auto">
          Die neuesten Trends im Glasmorphismus-Design kombinieren subtile Animationen, 
          Lichtreflexionen und tiefere Ebenen für einen naturalistischeren Effekt.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {/* Neo Glaskarten mit verschiedenen Effekten */}
          <NeoGlassCard className="p-8" variant="frost" animation="pulse" glare>
            <h2 className="text-2xl font-bold text-white mb-4">Pulsierender Frost-Effekt</h2>
            <p className="text-white/80 mb-6">
              Diese moderne Variante nutzt subtile Animationen, die die Transparenz und Unschärfe dynamisch verändern.
            </p>
            <GlassButton variant="blue">Mehr erfahren</GlassButton>
          </NeoGlassCard>
          
          <NeoGlassCard className="p-8" variant="smoke" animation="float" depth="deep">
            <h2 className="text-2xl font-bold text-white mb-4">Schwebender Rauch-Effekt</h2>
            <p className="text-white/80 mb-6">
              Eine dunklere Variante mit einer sanften Schwebeanimation, die Tiefe und Dimension verleiht.
            </p>
            <GlassButton variant="purple">Entdecken</GlassButton>
          </NeoGlassCard>
          
          <NeoGlassCard className="p-8" variant="gradient" animation="color-shift" glare>
            <h2 className="text-2xl font-bold text-white mb-4">Farbwechsel-Gradient</h2>
            <p className="text-white/80 mb-6">
              Diese Karte nutzt einen subtilen Farbwechsel am Rand, kombiniert mit einem Glanzeffekt.
            </p>
            <GlassButton variant="light">Aktivieren</GlassButton>
          </NeoGlassCard>
        </div>
        
        {/* Fortschrittliche Glaseffekte - Demo */}
        <div className="mb-16">
          <NeoGlassCard 
            className="p-10 relative" 
            variant="neo" 
            depth="deep" 
            animation="refract"
            glare
          >
            <div className="flex flex-col md:flex-row gap-8 items-center">
              <div className="flex-1">
                <h2 className="text-3xl font-bold text-white mb-6">Lichtbrechungs-Technologie</h2>
                <p className="text-white/80 mb-8 text-lg">
                  Die neueste Innovation im Glasmorphismus nutzt Lichtbrechungseffekte, 
                  die den Eindruck echter Glasoberflächen verstärken und auf Bewegungen reagieren.
                </p>
                <div className="flex flex-wrap gap-4">
                  <GlassButton variant="blue" size="lg">Demo ansehen</GlassButton>
                  <GlassButton variant="light" size="lg">Dokumentation</GlassButton>
                </div>
              </div>
              
              {/* Modernes 3D Element */}
              <div className="flex-1 flex justify-center">
                <div className="relative w-72 h-72">
                  {/* Mehrere überlagerte Glasschichten für 3D-Effekt */}
                  <div className="absolute inset-8 rounded-full bg-gradient-radial from-blue-500/40 to-transparent blur-md animate-float" style={{animationDelay: '-2s'}}></div>
                  <div className="absolute inset-16 rounded-full bg-gradient-radial from-purple-500/40 to-transparent blur-md animate-float" style={{animationDelay: '-1s'}}></div>
                  <div className="absolute inset-24 rounded-full bg-gradient-radial from-indigo-500/40 to-transparent blur-md animate-float"></div>
                  
                  {/* Zentrale Glasscheibe mit verstärktem Glanz */}
                  <div className="absolute inset-0 rounded-full backdrop-blur-xl bg-white/10 border border-white/20 animate-pulse-glass shadow-glass-highlight flex items-center justify-center">
                    <div className="text-white text-center">
                      <div className="text-5xl font-bold">2025</div>
                      <div className="text-lg opacity-70">Glasmorphismus</div>
                    </div>
                    
                    {/* Hochglanz-Effekt */}
                    <div className="absolute inset-0 rounded-full bg-gradient-to-b from-white/30 via-transparent to-transparent opacity-50"></div>
                  </div>
                </div>
              </div>
            </div>
          </NeoGlassCard>
        </div>
        
        {/* Feature Vergleichstabelle */}
        <div className="mb-16">
          <NeoGlassCard className="p-8 overflow-hidden" variant="frost">
            <h2 className="text-2xl font-bold text-white mb-6">Vergleich der Glasmorphismus-Techniken</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-white/80 border-collapse">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="py-3 px-4 text-left">Technik</th>
                    <th className="py-3 px-4 text-left">Performance</th>
                    <th className="py-3 px-4 text-left">Kompatibilität</th>
                    <th className="py-3 px-4 text-left">Visuelle Tiefe</th>
                    <th className="py-3 px-4 text-left">Umsetzbarkeit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="py-3 px-4 font-medium">Klassischer Glasmorphismus</td>
                    <td className="py-3 px-4">Gut</td>
                    <td className="py-3 px-4">Alle modernen Browser</td>
                    <td className="py-3 px-4">Mittel</td>
                    <td className="py-3 px-4">Einfach</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-3 px-4 font-medium">Animierter Glasmorphismus</td>
                    <td className="py-3 px-4">Mittel</td>
                    <td className="py-3 px-4">Chromium, Firefox, Safari</td>
                    <td className="py-3 px-4">Hoch</td>
                    <td className="py-3 px-4">Mittel</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="py-3 px-4 font-medium">Lichtbrechungs-Effekte</td>
                    <td className="py-3 px-4">Niedrig</td>
                    <td className="py-3 px-4">Neueste Browser</td>
                    <td className="py-3 px-4">Sehr hoch</td>
                    <td className="py-3 px-4">Komplex</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium">Neo-Glasmorphismus 2025</td>
                    <td className="py-3 px-4">Optimiert</td>
                    <td className="py-3 px-4">Alle Hauptbrowser</td>
                    <td className="py-3 px-4">Ultrahoch</td>
                    <td className="py-3 px-4">Modular</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </NeoGlassCard>
        </div>
        
        {/* Footer mit Glare-Effekt */}
        <NeoGlassCard className="p-6 text-center" variant="dark" glare>
          <p className="text-white/60">
            © 2025 Resume Matcher - Moderne Glasmorphismus-Trends Demonstration
          </p>
        </NeoGlassCard>
      </div>
    </div>
  );
}
