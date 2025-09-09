"use client";

import { useSession } from 'next-auth/react';
import Hero from '@/components/home/hero';
import FileUpload from '@/components/common/file-upload';

export default function HomePage() {
  const { data: session } = useSession();
  return (
    <>
      {/* Upload section pinned to top for immediate visibility */}
      <div className="w-full bg-blue-50 border-b border-blue-200">
        <div className="container mx-auto px-6 py-6">
          <div className="mx-auto w-full max-w-3xl rounded-xl border border-blue-200 bg-white p-4 shadow-sm md:p-6">
            <FileUpload session={session} />
          </div>
        </div>
      </div>

      {/* Hero below */}
      <Hero session={session} />
    </>
  );
}
