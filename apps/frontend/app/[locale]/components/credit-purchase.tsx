'use client'

import { useState, useTransition } from 'react'
import { useTranslations } from 'next-intl'
import { motion } from 'motion/react'
import { 
  CreditCard, 
  Zap, 
  Star, 
  Check, 
  Loader2, 
  Shield,
  ArrowRight 
} from 'lucide-react'
import { purchaseCredits } from '@/app/actions/credits'
import { CREDIT_PACKAGES } from '@/lib/stripe'

interface CreditPurchaseProps {
  locale?: string
  className?: string
  onPurchaseStart?: () => void
  onPurchaseError?: (error: string) => void
}

interface CreditPackage {
  id: string
  stripePriceId: string
  name: string
  credits: number
  priceInCents: number
  description: string
  popular: boolean
}

export function CreditPurchase({ 
  locale = 'en',
  className = '',
  onPurchaseStart,
  onPurchaseError
}: CreditPurchaseProps) {
  const t = useTranslations('Credits')
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  const handlePurchase = async (packageId: string) => {
    const creditPackage = CREDIT_PACKAGES.find(pkg => pkg.id === packageId)
    if (!creditPackage) return

    setSelectedPackage(packageId)
    onPurchaseStart?.()

    startTransition(async () => {
      try {
        const formData = new FormData()
        formData.append('priceId', creditPackage.stripePriceId)
        formData.append('quantity', '1')
        formData.append('locale', locale)

        await purchaseCredits(formData)
      } catch (error) {
        console.error('Purchase failed:', error)
        onPurchaseError?.(error instanceof Error ? error.message : 'Purchase failed')
        setSelectedPackage(null)
      }
    })
  }

  const formatPrice = (priceInCents: number) => {
    return new Intl.NumberFormat(locale === 'de' ? 'de-DE' : 'en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(priceInCents / 100)
  }

  const getValuePerCredit = (priceInCents: number, credits: number) => {
    const costPerCredit = priceInCents / credits
    return new Intl.NumberFormat(locale === 'de' ? 'de-DE' : 'en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 3,
      maximumFractionDigits: 3,
    }).format(costPerCredit / 100)
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-100 flex items-center justify-center gap-2">
          <Zap className="w-6 h-6 text-yellow-400" />
          {t('purchase.title', { default: 'Purchase Credits' })}
        </h2>
        <p className="text-gray-400 max-w-md mx-auto">
          {t('purchase.description', { 
            default: 'Choose the perfect credit package for your resume analysis and job matching needs.' 
          })}
        </p>
      </div>

      {/* Package Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {CREDIT_PACKAGES.map((pkg) => (
          <PackageCard
            key={pkg.id}
            package={pkg}
            locale={locale}
            isSelected={selectedPackage === pkg.id}
            isPending={isPending && selectedPackage === pkg.id}
            onSelect={() => handlePurchase(pkg.id)}
            formatPrice={formatPrice}
            getValuePerCredit={getValuePerCredit}
            t={t}
          />
        ))}
      </div>

      {/* Security Notice */}
      <div className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-3 text-gray-300">
          <Shield className="w-5 h-5 text-green-400" />
          <div>
            <h4 className="font-medium">{t('security.title', { default: 'Secure Payment' })}</h4>
            <p className="text-sm text-gray-400">
              {t('security.description', { 
                default: 'All payments are processed securely through Stripe. Your payment information is never stored on our servers.' 
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Usage Examples */}
      <div className="mt-8 space-y-4">
        <h3 className="text-lg font-semibold text-gray-200">
          {t('examples.title', { default: 'What can you do with credits?' })}
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <UsageExample
            icon="📄"
            title={t('examples.analysis.title', { default: 'Resume Analysis' })}
            description={t('examples.analysis.description', { default: 'Detailed analysis and scoring' })}
            cost={10}
          />
          <UsageExample
            icon="🎯"
            title={t('examples.matching.title', { default: 'Job Matching' })}
            description={t('examples.matching.description', { default: 'Find matching job opportunities' })}
            cost={5}
          />
          <UsageExample
            icon="✨"
            title={t('examples.improvement.title', { default: 'Resume Enhancement' })}
            description={t('examples.improvement.description', { default: 'AI-powered improvements' })}
            cost={15}
          />
        </div>
      </div>
    </div>
  )
}

// Package card component
function PackageCard({
  package: pkg,
  locale,
  isSelected,
  isPending,
  onSelect,
  formatPrice,
  getValuePerCredit,
  t
}: {
  package: CreditPackage
  locale: string
  isSelected: boolean
  isPending: boolean
  onSelect: () => void
  formatPrice: (price: number) => string
  getValuePerCredit: (price: number, credits: number) => string
  t: any
}) {
  const savings = pkg.id === 'premium' ? 20 : pkg.id === 'pro' ? 10 : 0

  return (
    <motion.div
      layout
      whileHover={{ scale: isPending ? 1 : 1.02 }}
      whileTap={{ scale: isPending ? 1 : 0.98 }}
      className={`relative p-6 rounded-xl border-2 transition-all cursor-pointer ${
        pkg.popular
          ? 'border-blue-500 bg-blue-900/20 shadow-blue-500/20 shadow-lg'
          : 'border-gray-700 bg-gray-900/50 hover:border-gray-600'
      } ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
      onClick={onSelect}
    >
      {/* Popular Badge */}
      {pkg.popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
            <Star className="w-3 h-3" />
            {t('packages.popular', { default: 'Most Popular' })}
          </div>
        </div>
      )}

      {/* Savings Badge */}
      {savings > 0 && (
        <div className="absolute top-4 right-4">
          <div className="bg-green-600 text-white px-2 py-1 rounded text-xs font-medium">
            {savings}% {t('packages.savings', { default: 'OFF' })}
          </div>
        </div>
      )}

      {/* Package Content */}
      <div className="space-y-4">
        {/* Header */}
        <div className="text-center">
          <h3 className="text-xl font-bold text-gray-100">{pkg.name}</h3>
          <div className="mt-2">
            <span className="text-3xl font-bold text-gray-100">
              {formatPrice(pkg.priceInCents)}
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            {getValuePerCredit(pkg.priceInCents, pkg.credits)} {t('packages.per_credit', { default: 'per credit' })}
          </p>
        </div>

        {/* Credits */}
        <div className="text-center py-4 bg-gray-800/50 rounded-lg">
          <div className="text-2xl font-bold text-yellow-400 flex items-center justify-center gap-2">
            <CreditCard className="w-6 h-6" />
            {pkg.credits.toLocaleString(locale)}
          </div>
          <div className="text-sm text-gray-400">
            {t('packages.credits', { default: 'Credits' })}
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-400 text-center">
          {pkg.description}
        </p>

        {/* Features */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-300">
            <Check className="w-4 h-4 text-green-400" />
            <span>{Math.floor(pkg.credits / 10)} {t('features.analyses', { default: 'Resume Analyses' })}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-300">
            <Check className="w-4 h-4 text-green-400" />
            <span>{Math.floor(pkg.credits / 5)} {t('features.matches', { default: 'Job Matches' })}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-300">
            <Check className="w-4 h-4 text-green-400" />
            <span>{Math.floor(pkg.credits / 15)} {t('features.improvements', { default: 'Resume Improvements' })}</span>
          </div>
        </div>

        {/* Purchase Button */}
        <motion.button
          whileHover={{ scale: isPending ? 1 : 1.05 }}
          whileTap={{ scale: isPending ? 1 : 0.95 }}
          disabled={isPending}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
            pkg.popular
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-700 hover:bg-gray-600 text-gray-100'
          } ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isPending && isSelected ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              {t('packages.processing', { default: 'Processing...' })}
            </>
          ) : (
            <>
              {t('packages.purchase', { default: 'Purchase Now' })}
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  )
}

// Usage example component
function UsageExample({
  icon,
  title,
  description,
  cost
}: {
  icon: string
  title: string
  description: string
  cost: number
}) {
  return (
    <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
      <div className="text-2xl mb-2">{icon}</div>
      <h4 className="font-medium text-gray-200">{title}</h4>
      <p className="text-sm text-gray-400 mb-2">{description}</p>
      <div className="text-sm font-medium text-yellow-400">
        -{cost} Credits
      </div>
    </div>
  )
}

export default CreditPurchase
