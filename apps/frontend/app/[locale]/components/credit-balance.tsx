'use client'

import { useState, useEffect } from 'react'
import { useTranslations } from 'next-intl'
import { motion } from 'motion/react'
import { CreditCard, TrendingUp, Clock, AlertCircle } from 'lucide-react'
import { getUserCreditSummary } from '@/app/actions/credits'

interface CreditBalanceProps {
  initialBalance?: number
  locale?: string
  showHistory?: boolean
  className?: string
}

interface CreditSummary {
  balance: number
  recentTransactions: Array<{
    id: string
    amount: number
    reason: string
    createdAt: Date
  }>
  costs: {
    resume_analysis: number
    job_match: number
    resume_improvement: number
  }
}

export function CreditBalance({ 
  initialBalance = 0, 
  locale = 'en',
  showHistory = true,
  className = ''
}: CreditBalanceProps) {
  const t = useTranslations('Credits')
  const [summary, setSummary] = useState<CreditSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadCreditSummary() {
      try {
        setLoading(true)
        const result = await getUserCreditSummary()
        if (result.success) {
          setSummary({
            balance: result.balance,
            recentTransactions: result.recentTransactions,
            costs: result.costs
          })
        }
      } catch (err) {
        console.error('Failed to load credit summary:', err)
        setError(err instanceof Error ? err.message : 'Failed to load credits')
      } finally {
        setLoading(false)
      }
    }

    loadCreditSummary()
  }, [])

  const balance = summary?.balance ?? initialBalance

  if (loading) {
    return (
      <div className={`bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-6 bg-gray-600 rounded"></div>
            <div className="h-6 bg-gray-600 rounded w-32"></div>
          </div>
          <div className="h-8 bg-gray-600 rounded w-24 mb-2"></div>
          <div className="h-4 bg-gray-600 rounded w-40"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-red-900/20 backdrop-blur-sm p-6 rounded-lg border border-red-700 ${className}`}>
        <div className="flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <div>
            <h3 className="font-medium">{t('error.title', { default: 'Failed to load credits' })}</h3>
            <p className="text-sm text-red-300">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700 ${className}`}>
      {/* Current Balance */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-blue-600/20 rounded-lg">
          <CreditCard className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <p className="text-sm text-gray-400">{t('balance.current', { default: 'Current Balance' })}</p>
          <motion.div
            key={balance}
            initial={{ scale: 1.2, color: '#60A5FA' }}
            animate={{ scale: 1, color: '#F3F4F6' }}
            transition={{ duration: 0.3 }}
            className="text-2xl font-bold text-gray-100"
          >
            {balance.toLocaleString(locale)} {t('unit', { default: 'Credits' })}
          </motion.div>
        </div>
      </div>

      {/* Credit Costs */}
      {summary?.costs && (
        <div className="space-y-3 mb-6">
          <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            {t('usage.title', { default: 'Feature Costs' })}
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <FeatureCost
              feature="resume_analysis"
              cost={summary.costs.resume_analysis}
              title={t('usage.resume_analysis', { default: 'Resume Analysis' })}
              canAfford={balance >= summary.costs.resume_analysis}
            />
            <FeatureCost
              feature="job_match"
              cost={summary.costs.job_match}
              title={t('usage.job_match', { default: 'Job Matching' })}
              canAfford={balance >= summary.costs.job_match}
            />
            <FeatureCost
              feature="resume_improvement"
              cost={summary.costs.resume_improvement}
              title={t('usage.resume_improvement', { default: 'Resume Improvement' })}
              canAfford={balance >= summary.costs.resume_improvement}
            />
          </div>
        </div>
      )}

      {/* Recent Transactions */}
      {showHistory && summary?.recentTransactions && summary.recentTransactions.length > 0 && (
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2 mb-3">
            <Clock className="w-4 h-4" />
            {t('history.title', { default: 'Recent Activity' })}
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {summary.recentTransactions.slice(0, 5).map((transaction) => (
              <TransactionItem
                key={transaction.id}
                transaction={transaction}
                locale={locale}
              />
            ))}
          </div>
        </div>
      )}

      {/* Low Balance Warning */}
      {balance < Math.max(summary?.costs.resume_analysis ?? 10, summary?.costs.job_match ?? 5) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 bg-yellow-900/20 border border-yellow-700 rounded-lg"
        >
          <div className="flex items-center gap-2 text-yellow-400">
            <AlertCircle className="w-4 h-4" />
            <p className="text-sm">
              {t('warning.low_balance', { 
                default: 'Low credit balance. Consider purchasing more credits to continue using features.',
                balance 
              })}
            </p>
          </div>
        </motion.div>
      )}
    </div>
  )
}

// Feature cost display component
function FeatureCost({ 
  feature, 
  cost, 
  title, 
  canAfford 
}: { 
  feature: string
  cost: number
  title: string
  canAfford: boolean 
}) {
  return (
    <div className={`p-3 rounded-lg border ${
      canAfford 
        ? 'bg-green-900/20 border-green-700 text-green-300' 
        : 'bg-red-900/20 border-red-700 text-red-300'
    }`}>
      <div className="text-xs font-medium opacity-80">{title}</div>
      <div className="text-lg font-bold">-{cost}</div>
    </div>
  )
}

// Transaction item component
function TransactionItem({ 
  transaction, 
  locale 
}: { 
  transaction: {
    id: string
    amount: number
    reason: string
    createdAt: Date
  }
  locale: string 
}) {
  const t = useTranslations('Credits.reasons')
  
  const getReasonDisplay = (reason: string) => {
    switch (reason) {
      case 'purchase':
        return t('purchase', { default: 'Credit Purchase' })
      case 'refund':
        return t('refund', { default: 'Refund' })
      case 'resume_analysis':
        return t('resume_analysis', { default: 'Resume Analysis' })
      case 'job_match':
        return t('job_match', { default: 'Job Matching' })
      case 'resume_improvement':
        return t('resume_improvement', { default: 'Resume Improvement' })
      case 'welcome':
        return t('welcome', { default: 'Welcome Bonus' })
      case 'bonus':
        return t('bonus', { default: 'Bonus Credits' })
      default:
        return reason
    }
  }

  const isPositive = transaction.amount > 0
  
  return (
    <div className="flex items-center justify-between p-2 rounded border border-gray-700/50">
      <div className="flex-1">
        <div className="text-sm text-gray-300">{getReasonDisplay(transaction.reason)}</div>
        <div className="text-xs text-gray-500">
          {new Date(transaction.createdAt).toLocaleDateString(locale, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
      <div className={`font-medium ${
        isPositive ? 'text-green-400' : 'text-red-400'
      }`}>
        {isPositive ? '+' : ''}{transaction.amount}
      </div>
    </div>
  )
}

export default CreditBalance
