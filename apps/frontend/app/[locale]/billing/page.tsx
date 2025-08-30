import { auth } from "@/auth";
import { redirect } from "next/navigation";
import BillingPageClient from '@/app/billing/page';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

interface PageProps {
  params: Promise<{ locale: string }>;
}

export default async function BillingPage({ params }: PageProps) {
  const { locale } = await params;
  const session = await auth();
  
  if (!session) {
    redirect(`/${locale}/login`);
  }
  
  return <BillingPageClient />;
}
