"use client";
import { useEffect } from 'react';
import { signIn, getSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      const session = await getSession();
      if (session) {
        router.push('/dashboard');
        return;
      }
      
      // Automatically trigger Google sign-in
      signIn('google', { callbackUrl: '/dashboard' });
    };

    checkSession();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="space-y-4 text-center max-w-md">
        <div className="text-xl font-semibold">Resume Matcher</div>
        <div className="text-sm text-muted-foreground">
          Redirecting to Google Sign-In...
        </div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <div className="text-xs text-muted-foreground">
          If you're not redirected automatically, please wait a moment.
        </div>
      </div>
    </div>
  );
}
