"use client";
import { useEffect, useState } from 'react';
import { SignIn, ClerkLoaded, ClerkLoading } from '@clerk/nextjs';

export default function Page() {
  const [slow, setSlow] = useState(false);
  // Consider both public and server variants; ClerkProvider may receive the server variant.
  const hasPk = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || process.env.CLERK_PUBLISHABLE_KEY);
  useEffect(() => {
    const t = setTimeout(() => setSlow(true), 6000);
    return () => clearTimeout(t);
  }, []);
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {!hasPk && (
        <div className="mb-3 rounded-md border border-red-600/40 bg-red-900/20 p-3 text-red-200 text-sm max-w-md">
          <div className="font-medium mb-1">Fehlende Konfiguration</div>
          <ul className="list-disc text-left ml-5 space-y-1">
            <li>Clerk Publishable Key fehlt. Setze NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (oder CLERK_PUBLISHABLE_KEY) in deinen Umgebungsvariablen.</li>
            <li>Im Frontend-Host (z. B. Vercel: Project → Settings → Environment Variables) setzen und redeployen.</li>
          </ul>
        </div>
      )}
      <ClerkLoading>
        <div className="space-y-2 text-sm text-muted-foreground text-center max-w-md">
          <div>Lade Anmeldung…</div>
          {slow && (
            <div className="mt-3 rounded-md border border-yellow-600/40 bg-yellow-900/20 p-3 text-yellow-200">
              <div className="font-medium mb-1">Hinweis:</div>
              <ul className="list-disc text-left ml-5 space-y-1">
                <li>Custom Domains in Clerk noch nicht verifiziert (SSL ausstehend).</li>
                <li>Stelle sicher: Publishable Key ist gesetzt (NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY oder CLERK_PUBLISHABLE_KEY).</li>
                <li>CSP erlaubt *.clerk.com / *.clerk.services und deine Custom Domains.</li>
              </ul>
            </div>
          )}
        </div>
      </ClerkLoading>
      <ClerkLoaded>
        <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" />
      </ClerkLoaded>
    </div>
  );
}
