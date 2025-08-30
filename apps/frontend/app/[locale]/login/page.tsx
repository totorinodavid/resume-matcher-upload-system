"use client";

import { signIn, useSession } from 'next-auth/react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { useEffect } from 'react';
import BackgroundContainer from '@/components/common/background-container';

export default function LoginPage() {
  const t = useTranslations('Login');
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const locale = (params?.locale as string) || 'en';

  // Redirect if already authenticated
  useEffect(() => {
    if (status === 'authenticated' && session) {
      router.push(`/${locale}/dashboard`);
    }
  }, [status, session, router, locale]);

  const handleGoogleSignIn = () => {
    signIn('google', { 
      callbackUrl: `/${locale}/dashboard`,
      redirect: true
    });
  };

  // Show loading state while checking session
  if (status === 'loading') {
    return (
      <BackgroundContainer className="min-h-screen flex items-center justify-center">
        <div className="bg-zinc-900 p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-center text-white">Loading...</div>
        </div>
      </BackgroundContainer>
    );
  }

  // Don't render if already authenticated (will redirect)
  if (status === 'authenticated') {
    return null;
  }

  return (
    <BackgroundContainer className="min-h-screen flex items-center justify-center">
      <div className="bg-zinc-900 p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-2xl font-bold text-center mb-6 text-white">
          {t('title', { default: 'Sign In' })}
        </h1>
        <p className="text-gray-400 text-center mb-8">
          {t('subtitle', { default: 'Sign in to your account to continue' })}
        </p>
        <button
          onClick={handleGoogleSignIn}
          className="w-full bg-white text-gray-900 py-3 px-4 rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {t('continueWithGoogle', { default: 'Continue with Google' })}
        </button>
      </div>
    </BackgroundContainer>
  );
}
