"use client";
import { useUser, useAuth } from "@clerk/nextjs";

export default function DebugAuthPage() {
  const { isSignedIn, user } = useUser();
  const { orgId, sessionId, getToken } = useAuth();
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">Auth Debug</h1>
      <div className="rounded-md border border-zinc-800 bg-zinc-900 p-4 text-sm">
        <div><b>signedIn:</b> {String(isSignedIn)}</div>
        <div><b>sessionId:</b> {sessionId ?? "null"}</div>
        <div><b>orgId:</b> {orgId ?? "null"}</div>
        <div><b>userId:</b> {user?.id ?? "null"}</div>
        <div><b>email:</b> {user?.primaryEmailAddress?.emailAddress ?? "null"}</div>
      </div>
      <button
        className="rounded bg-indigo-600 px-3 py-1.5 text-white"
        onClick={async () => {
          try {
            const token = await getToken({ template: process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || undefined });
            if (!token) alert("No token returned. Check Clerk JWT template.");
            else alert(token.slice(0, 24) + "…" + token.slice(-8));
          } catch (e: any) {
            alert("getToken error: " + (e?.message || String(e)));
          }
        }}
      >Mint Backend Token</button>
      <div className="text-xs opacity-70">
        If signed in client-side but API says unauthorized, verify Vercel envs:
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (client) and CLERK_SECRET_KEY (server).
      </div>
    </div>
  );
}
