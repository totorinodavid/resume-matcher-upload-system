import { auth } from "@/auth";
import { redirect } from "next/navigation";
import ResumeUploadPageClient from '@/components/pages/resume-upload.client';

// Ensure this route always reflects current auth/session and avoids ISR for JSON data route.
export const dynamic = 'force-dynamic';
export const revalidate = 0;

interface PageProps {
  params: Promise<{ locale: string }>;
}

export default async function ResumeUploadPage({ params }: PageProps) {
  const { locale } = await params;
  const session = await auth();
  
  if (!session) {
    redirect(`/${locale}/login`);
  }
  
  return <ResumeUploadPageClient session={session} />;
}
