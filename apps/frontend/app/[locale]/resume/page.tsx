import { auth } from "@/auth";
import { redirect } from "next/navigation";
import ResumeUploadPageClient from '@/components/pages/resume-upload.client';

// Ensure this route always reflects current auth/session and avoids ISR for JSON data route.
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function ResumeUploadPage() {
  const session = await auth();
  if (!session) {
    redirect("/login");
  }
  return <ResumeUploadPageClient session={session} />;
}
