import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import { getTranslations } from "next-intl/server";
import { Metadata } from "next";
import CreditBalance from "@/app/[locale]/components/credit-balance";
import CreditPurchase from "@/app/[locale]/components/credit-purchase";
import CreditHistory from "@/app/[locale]/components/credit-history";
import { CheckCircle, XCircle, AlertCircle, Sparkles } from "lucide-react";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

interface PageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'Credits' });
  
  return {
    title: t('meta.title', { default: 'Credits & Billing | Resume Matcher' }),
    description: t('meta.description', { 
      default: 'Manage your credits, purchase credit packages, and view your billing history for Resume Matcher services.' 
    }),
  };
}

export default async function BillingPage({ params, searchParams }: PageProps) {
  const { locale } = await params;
  const session = await auth();
  const search = await searchParams;
  
  if (!session) {
    redirect(`/${locale}/login`);
  }

  const t = await getTranslations('Credits');
  
  // Handle payment status messages
  const success = search.success === 'true';
  const canceled = search.canceled === 'true';
  const error = search.error;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-8 h-8 text-yellow-400" />
            <h1 className="text-4xl font-bold text-gray-100">
              {t('page.title', { default: 'Credits & Billing' })}
            </h1>
          </div>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            {t('page.description', { 
              default: 'Manage your Resume Matcher credits, purchase additional credits, and track your usage history.' 
            })}
          </p>
        </div>

        {/* Status Messages */}
        {success && (
          <div className="mb-8 p-4 bg-green-900/20 border border-green-700 rounded-lg">
            <div className="flex items-center gap-3 text-green-400">
              <CheckCircle className="w-5 h-5" />
              <div>
                <h3 className="font-medium">{t('status.success.title', { default: 'Payment Successful!' })}</h3>
                <p className="text-sm text-green-300">
                  {t('status.success.message', { 
                    default: 'Your credits have been added to your account. You can now use Resume Matcher features.' 
                  })}
                </p>
              </div>
            </div>
          </div>
        )}

        {canceled && (
          <div className="mb-8 p-4 bg-yellow-900/20 border border-yellow-700 rounded-lg">
            <div className="flex items-center gap-3 text-yellow-400">
              <AlertCircle className="w-5 h-5" />
              <div>
                <h3 className="font-medium">{t('status.canceled.title', { default: 'Payment Canceled' })}</h3>
                <p className="text-sm text-yellow-300">
                  {t('status.canceled.message', { 
                    default: 'Your payment was canceled. No charges were made to your account.' 
                  })}
                </p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-8 p-4 bg-red-900/20 border border-red-700 rounded-lg">
            <div className="flex items-center gap-3 text-red-400">
              <XCircle className="w-5 h-5" />
              <div>
                <h3 className="font-medium">{t('status.error.title', { default: 'Payment Error' })}</h3>
                <p className="text-sm text-red-300">
                  {t('status.error.message', { 
                    default: 'There was an error processing your payment. Please try again or contact support.',
                    error: error as string
                  })}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Balance & Purchase */}
          <div className="lg:col-span-2 space-y-8">
            {/* Credit Balance */}
            <Suspense fallback={<CreditBalanceSkeleton />}>
              <CreditBalance 
                locale={locale}
                showHistory={false}
                className="w-full"
              />
            </Suspense>

            {/* Credit Purchase */}
            <Suspense fallback={<CreditPurchaseSkeleton />}>
              <CreditPurchaseSection locale={locale} />
            </Suspense>
          </div>

          {/* Right Column - History */}
          <div className="lg:col-span-1">
            <Suspense fallback={<CreditHistorySkeleton />}>
              <CreditHistory 
                locale={locale}
                className="w-full"
                showFilters={true}
                maxTransactions={20}
              />
            </Suspense>
          </div>
        </div>

        {/* Additional Information */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoCard
            title={t('info.security.title', { default: 'Secure Payments' })}
            description={t('info.security.description', { 
              default: 'All payments are processed securely through Stripe with industry-standard encryption.' 
            })}
            icon="🔒"
          />
          <InfoCard
            title={t('info.refunds.title', { default: 'Refund Policy' })}
            description={t('info.refunds.description', { 
              default: 'Unused credits can be refunded within 30 days of purchase. Contact support for assistance.' 
            })}
            icon="💰"
          />
          <InfoCard
            title={t('info.support.title', { default: 'Need Help?' })}
            description={t('info.support.description', { 
              default: 'Our support team is available 24/7 to help with any billing or credit-related questions.' 
            })}
            icon="💬"
          />
        </div>
      </div>
    </div>
  );
}

// Credit Purchase Section with error handling
function CreditPurchaseSection({ locale }: { locale: string }) {
  return (
    <div className="bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
      <CreditPurchase 
        locale={locale}
        onPurchaseStart={() => {
          // Optional: Show loading state or tracking
          console.log('Purchase started');
        }}
        onPurchaseError={(error) => {
          // Optional: Show error toast or notification
          console.error('Purchase error:', error);
        }}
      />
    </div>
  );
}

// Info card component
function InfoCard({ 
  title, 
  description, 
  icon 
}: { 
  title: string
  description: string
  icon: string 
}) {
  return (
    <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700/50">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-100 mb-2">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  );
}

// Loading skeletons
function CreditBalanceSkeleton() {
  return (
    <div className="bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
      <div className="animate-pulse">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gray-600 rounded-lg"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-600 rounded w-24"></div>
            <div className="h-6 bg-gray-600 rounded w-32"></div>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-600 rounded"></div>
          ))}
        </div>
        <div className="h-4 bg-gray-600 rounded w-48"></div>
      </div>
    </div>
  );
}

function CreditPurchaseSkeleton() {
  return (
    <div className="bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
      <div className="animate-pulse">
        <div className="text-center mb-6">
          <div className="h-8 bg-gray-600 rounded w-48 mx-auto mb-2"></div>
          <div className="h-4 bg-gray-600 rounded w-64 mx-auto"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-600 rounded-lg"></div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CreditHistorySkeleton() {
  return (
    <div className="bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
      <div className="animate-pulse">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-6 h-6 bg-gray-600 rounded"></div>
          <div className="h-6 bg-gray-600 rounded w-32"></div>
        </div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-gray-800 rounded">
              <div className="space-y-2">
                <div className="h-4 bg-gray-600 rounded w-24"></div>
                <div className="h-3 bg-gray-600 rounded w-16"></div>
              </div>
              <div className="h-5 bg-gray-600 rounded w-12"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
