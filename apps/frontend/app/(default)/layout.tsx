import { auth } from "@/auth";
import { LogoutButton } from "@/components/logout-button";
import Link from 'next/link';
import { ResumePreviewProvider } from '@/components/common/resume_previewer_context';

async function AuthHeader() {
  const session = await auth();

  return (
    <>
      {session?.user ? (
        <LogoutButton />
      ) : (
        <Link href="/login" className="rounded-md px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm">Sign in</Link>
      )}
    </>
  );
}

export default function DefaultLayout({ children }: { children: React.ReactNode }) {
  return (
    <ResumePreviewProvider>
      <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
        <Link href="/billing" data-testid="nav-billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
        <AuthHeader />
      </div>
      <main className="min-h-screen flex flex-col">{children}</main>
    </ResumePreviewProvider>
  );
}
