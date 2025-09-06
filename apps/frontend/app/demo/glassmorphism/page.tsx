import React from 'react';
import { GlassCard, GlassButton, GlassInput, GlassContainer } from '@/components/ui/glass';

export default function GlassmorphismDemo() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-800 p-8">
      {/* Decorative orbs for background effect */}
      <div className="fixed -top-20 -left-20 w-96 h-96 rounded-full bg-blue-500/30 blur-3xl"></div>
      <div className="fixed top-1/3 -right-20 w-80 h-80 rounded-full bg-purple-500/30 blur-3xl"></div>
      <div className="fixed -bottom-20 left-1/3 w-72 h-72 rounded-full bg-indigo-500/30 blur-3xl"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <h1 className="text-4xl font-bold text-white text-center mb-12">Resume Matcher Glassmorphism UI</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Card 1: Default Glass Card */}
          <GlassCard className="p-6" hoverEffect>
            <h2 className="text-xl font-bold text-white mb-4">Resume Parsing</h2>
            <p className="text-white/80 mb-6">
              Upload your resume and let our AI analyze it for optimal job matching.
            </p>
            <GlassButton variant="blue" fullWidth>
              Upload Resume
            </GlassButton>
          </GlassCard>
          
          {/* Card 2: Dark Glass Card */}
          <GlassCard className="p-6" variant="dark" intensity="strong" hoverEffect>
            <h2 className="text-xl font-bold text-white mb-4">Job Matching</h2>
            <p className="text-white/80 mb-4">
              Find the perfect match for your skills and experience.
            </p>
            <div className="mb-4">
              <GlassInput 
                name="job-search" 
                placeholder="Enter job title..." 
                variant="blue"
                fullWidth
              />
            </div>
            <GlassButton variant="purple" fullWidth>
              Find Jobs
            </GlassButton>
          </GlassCard>
          
          {/* Card 3: Blue Glass Card */}
          <GlassCard className="p-6" variant="blue" hoverEffect>
            <h2 className="text-xl font-bold text-white mb-4">ATS Optimization</h2>
            <p className="text-white/80 mb-6">
              Improve your resume's ATS compatibility score with our AI tools.
            </p>
            <div className="flex flex-col space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-white">Keyword match</span>
                <span className="text-white font-bold">85%</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-white">Format score</span>
                <span className="text-white font-bold">92%</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '92%' }}></div>
              </div>
            </div>
          </GlassCard>
          
          {/* Larger feature card */}
          <GlassContainer className="col-span-1 md:col-span-2 lg:col-span-3 mt-8" intensity="strong" animated>
            <GlassCard className="p-8 border-none" variant="purple">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-white mb-4">
                    Premium Resume Analysis
                  </h2>
                  <p className="text-white/80 mb-6">
                    Get a comprehensive analysis of your resume with detailed feedback and suggestions for improvement.
                    Our AI will identify missing keywords, suggest format improvements, and help you optimize for ATS compatibility.
                  </p>
                  <div className="flex flex-wrap gap-4">
                    <GlassButton variant="light" size="lg">
                      Try Free Demo
                    </GlassButton>
                    <GlassButton variant="blue" size="lg">
                      Get Premium
                    </GlassButton>
                  </div>
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="w-64 h-64 rounded-full bg-gradient-to-tr from-purple-500/50 to-blue-500/50 flex items-center justify-center shadow-glass-purple">
                    <div className="text-white text-center">
                      <div className="text-4xl font-bold">95%</div>
                      <div className="text-lg">Success Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            </GlassCard>
          </GlassContainer>
          
          {/* Footer */}
          <div className="col-span-1 md:col-span-2 lg:col-span-3 mt-8">
            <GlassCard className="p-4 text-center" variant="dark">
              <p className="text-white/60">
                © 2025 Resume Matcher - Modern Glassmorphism UI Demo
              </p>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
