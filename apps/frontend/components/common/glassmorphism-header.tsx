"use client";

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { LogoutButton } from '@/components/logout-button';
import { LanguageDropdown } from '@/components/common/language-dropdown';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import { NeoGlassCard } from '@/components/ui/glass';

export function GlassmorphismHeader() {
  const { data: session } = useSession();
  const t = useTranslations('Header');
  const params = useParams();
  const locale = (params?.locale as string) || 'en';

  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full">
      {/* Modern Glassmorphism container using NeoGlassCard */}
      <NeoGlassCard
        variant="frost" 
        depth="flat" 
        animation="refract" 
        glare
        className="w-full border-b border-white/15 px-0 py-0"
      >
        {/* Content container */}
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo section with modern glass effect */}
            <Link 
              href={`/${locale}`} 
              className="flex items-center space-x-3 group transition-all duration-300 hover:scale-105"
            >
              {/* Logo icon with neo glassmorphism effect */}
              <div className="relative">
                <div className="w-12 h-12 rounded-xl overflow-hidden shadow-glass-neo">
                  {/* Background layers for depth */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/30 to-blue-500/30 backdrop-blur-md"></div>
                  <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent opacity-50"></div>
                  <div className="absolute inset-0 border border-white/20"></div>
                  
                  {/* Pulsing animation for the logo background */}
                  <div className="absolute inset-0 bg-gradient-radial from-white/20 to-transparent animate-pulse-glass opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  
                  {/* Logo image */}
                  <div className="relative z-10 w-full h-full flex items-center justify-center">
                    <Image 
                      src="/LOGO.png"
                      alt="Resume Matcher Logo"
                      width={32}
                      height={32}
                      className="object-contain transform group-hover:scale-110 transition-transform duration-300"
                    />
                  </div>
                </div>
                
                {/* Modern glow effect */}
                <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-purple-500/20 blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-color-shift" />
              </div>
              
              {/* Brand name with text effects */}
              <div className="flex flex-col">
                <div className="relative">
                  <Image 
                    src="/wort_logo.png"
                    alt="Resume Matcher"
                    width={120}
                    height={32}
                    className="object-contain relative z-10"
                  />
                  {/* Text glow effect on hover */}
                  <div className="absolute -inset-1 bg-blue-500/10 filter blur-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                <span className="text-xs bg-gradient-to-r from-gray-200 to-gray-400 bg-clip-text text-transparent font-medium -mt-1">
                  AI-Powered Job Matching
                </span>
              </div>
            </Link>

            {/* Navigation and actions */}
            <div className="flex items-center space-x-4">
              {/* Navigation links */}
              {session?.user && (
                <nav className="hidden md:flex items-center space-x-6">
                  <Link 
                    href={`/${locale}/dashboard`}
                    className="text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200 relative group"
                  >
                    {/* Text with hover effect */}
                    <span className="relative">
                      {t('dashboard', { default: 'Dashboard' })}
                      
                      {/* Gradient line with animation */}
                      <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 group-hover:w-full transition-all duration-300" />
                      
                      {/* Subtle glow effect on hover */}
                      <span className="absolute -inset-1 rounded-md bg-white/5 opacity-0 group-hover:opacity-100 transition-all duration-300 blur-sm" />
                    </span>
                  </Link>
                  
                  <Link 
                    href={`/${locale}/resume`}
                    className="text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200 relative group"
                  >
                    {/* Text with hover effect */}
                    <span className="relative">
                      {t('resume', { default: 'Resume' })}
                      
                      {/* Gradient line with animation */}
                      <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 group-hover:w-full transition-all duration-300" />
                      
                      {/* Subtle glow effect on hover */}
                      <span className="absolute -inset-1 rounded-md bg-white/5 opacity-0 group-hover:opacity-100 transition-all duration-300 blur-sm" />
                    </span>
                  </Link>
                </nav>
              )}

              {/* Language dropdown with glassmorphism */}
              <LanguageDropdown />

              {/* Authentication section */}
              {session?.user ? (
                <div className="flex items-center space-x-3">
                  {/* User avatar with neo glassmorphism */}
                  <div className="relative group">
                    {/* Neo glass container with hover effects */}
                    <div className="relative overflow-hidden rounded-lg px-3 py-2">
                      {/* Glass background */}
                      <div className="absolute inset-0 bg-white/10 backdrop-blur-md border border-white/15 shadow-glass-highlight group-hover:bg-white/15 transition-all duration-300"></div>
                      
                      {/* Subtle reflection */}
                      <div className="absolute inset-0 bg-gradient-to-b from-white/15 via-transparent to-transparent opacity-50"></div>
                      
                      {/* Shimmer effect */}
                      <div className="absolute -inset-full h-full w-1/2 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 transform -translate-x-full group-hover:translate-x-[200%] transition-transform duration-1000"></div>
                      
                      {/* Content */}
                      <div className="flex items-center space-x-2 relative z-10">
                        {/* Modern avatar with glow effect */}
                        <div className="relative">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-sm font-medium shadow-glass-purple">
                            {session.user.name?.[0] || session.user.email?.[0] || 'U'}
                          </div>
                          <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-purple-500/30 to-blue-500/30 opacity-0 group-hover:opacity-100 blur-md transition-opacity duration-300"></div>
                        </div>
                        
                        {/* Username with gradient text */}
                        <span className="text-sm text-white hidden md:block">
                          <span className="bg-gradient-to-r from-gray-100 to-gray-300 bg-clip-text text-transparent font-medium">
                            {session.user.name || session.user.email}
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Logout button with neo glassmorphism */}
                  <div className="relative overflow-hidden rounded-lg group">
                    {/* Glass container styling for LogoutButton */}
                    <div className="absolute inset-0 bg-white/5 backdrop-blur-md border border-white/15 group-hover:bg-white/10 transition-all duration-300 shadow-glass-highlight"></div>
                    
                    {/* Color shifting border effect */}
                    <div className="absolute inset-0 border border-white/20 rounded-lg opacity-0 group-hover:opacity-100 animate-color-shift"></div>
                    
                    {/* LogoutButton component */}
                    <div className="relative z-10">
                      <LogoutButton />
                    </div>
                  </div>
                  
                  {/* Debug link with neo glassmorphism */}
                  {(process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_SHOW_DEBUG === '1') && (
                    <Link 
                      href="/api/bff/api/v1/auth/whoami" 
                      target="_blank" 
                      className="relative px-2 py-1 rounded overflow-hidden group"
                    >
                      <div className="absolute inset-0 bg-white/5 backdrop-blur-md border border-white/10 group-hover:bg-white/10 transition-all duration-300"></div>
                      <span className="relative z-10 text-xs text-gray-400 group-hover:text-gray-300">Debug</span>
                    </Link>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  {/* Sign in button with neo glassmorphism */}
                  <Link 
                    href={`/${locale}/login`}
                    className="relative px-4 py-2 rounded-lg overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-white/10 backdrop-blur-md border border-white/20 group-hover:bg-white/15 transition-all duration-300 shadow-glass"></div>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 animate-shimmer"></div>
                    <span className="relative z-10 text-white text-sm font-medium">{t('signIn', { default: 'Sign In' })}</span>
                  </Link>
                  
                  {/* Upload CV button with advanced glass effect */}
                  <Link 
                    href={`/${locale}/resume`}
                    className="relative flex items-center space-x-2 px-4 py-2 rounded-lg overflow-hidden group"
                  >
                    {/* Base glass background */}
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/80 to-blue-500/80 backdrop-blur-md border border-white/30 shadow-glass-highlight transition-all duration-300 group-hover:shadow-glass-purple"></div>
                    
                    {/* Light reflection effect */}
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/30 to-transparent opacity-30 group-hover:opacity-50 transition-opacity duration-500"></div>
                    
                    {/* Shimmer animation */}
                    <div className="absolute -inset-full bg-gradient-to-r from-transparent via-white/20 to-transparent rotate-45 transform translate-x-[-100%] animate-[shimmer_2.5s_infinite]"></div>
                    
                    {/* Button content */}
                    <svg 
                      className="relative z-10 w-4 h-4" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth={2} 
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                      />
                    </svg>
                    <span className="relative z-10 text-white text-sm font-medium">{t('uploadCv', { default: 'Upload CV' })}</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </NeoGlassCard>
    </header>
  );
}
