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
      {/* Simple white header */}
      <div className="w-full bg-white border-b border-gray-200 shadow-sm">
        {/* Content container */}
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo section */}
            <Link 
              href={`/${locale}`} 
              className="flex items-center space-x-3 group transition-all duration-300"
            >
              {/* Logo icon */}
              <div className="relative">
                <div className="w-12 h-12 rounded-xl overflow-hidden bg-blue-600 flex items-center justify-center">
                  {/* Logo image */}
                  <Image 
                    src="/LOGO.png"
                    alt="Resume Matcher Logo"
                    width={32}
                    height={32}
                    className="object-contain"
                  />
                </div>
              </div>
              
              {/* Brand name */}
              <div className="flex flex-col">
                <div className="relative">
                  <Image 
                    src="/wort_logo.png"
                    alt="Resume Matcher"
                    width={120}
                    height={32}
                    className="object-contain"
                  />
                </div>
                <span className="text-xs text-gray-600 font-medium -mt-1">
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
                    className="text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors duration-200"
                  >
                    {t('dashboard', { default: 'Dashboard' })}
                  </Link>
                  
                  <Link 
                    href={`/${locale}/resume`}
                    className="text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors duration-200"
                  >
                    {t('resume', { default: 'Resume' })}
                  </Link>
                </nav>
              )}

              {/* Language dropdown */}
              <LanguageDropdown />

              {/* Authentication section */}
              {session?.user ? (
                <div className="flex items-center space-x-3">
                  {/* User avatar */}
                  <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-200">
                    {/* Avatar */}
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
                      {session.user.name?.[0] || session.user.email?.[0] || 'U'}
                    </div>
                    
                    {/* Username */}
                    <span className="text-sm text-gray-900 hidden md:block font-medium">
                      {session.user.name || session.user.email}
                    </span>
                  </div>
                  
                  {/* Logout button */}
                  <div className="px-3 py-2 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                    <LogoutButton />
                  </div>
                  
                  {/* Debug link */}
                  {(process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_SHOW_DEBUG === '1') && (
                    <Link 
                      href="/api/bff/api/v1/auth/whoami" 
                      target="_blank" 
                      className="px-2 py-1 rounded text-xs text-gray-500 hover:text-gray-700 border border-gray-200 hover:bg-gray-50 transition-colors"
                    >
                      Debug
                    </Link>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  {/* Sign in button */}
                  <Link 
                    href={`/${locale}/login`}
                    className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors text-sm font-medium"
                  >
                    {t('signIn', { default: 'Sign In' })}
                  </Link>
                  
                  {/* Upload CV button */}
                  <Link 
                    href={`/${locale}/resume`}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    <svg 
                      className="w-4 h-4" 
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
                    <span>{t('uploadCv', { default: 'Upload CV' })}</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
