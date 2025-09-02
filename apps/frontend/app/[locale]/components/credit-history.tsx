'use client'

import { useState, useEffect } from 'react'
import { useTranslations } from 'next-intl'
import { motion, AnimatePresence } from 'motion/react'
import { 
  History, 
  TrendingUp, 
  TrendingDown, 
  Filter,
  Calendar,
  CreditCard,
  RefreshCw,
  AlertCircle,
  ChevronDown,
  Download
} from 'lucide-react'
import { getUserCreditSummary } from '@/app/actions/credits'

interface CreditHistoryProps {
  locale?: string
  className?: string
  showFilters?: boolean
  maxTransactions?: number
}

interface Transaction {
  id: string
  amount: number
  reason: string
  createdAt: Date
  metadata?: any
}

type TransactionFilter = 'all' | 'purchase' | 'spend' | 'refund'

export function CreditHistory({ 
  locale = 'en',
  className = '',
  showFilters = true,
  maxTransactions = 50
}: CreditHistoryProps) {
  const t = useTranslations('Credits')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<TransactionFilter>('all')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const loadTransactions = async (refresh = false) => {
    try {
      if (refresh) setIsRefreshing(true)
      else setLoading(true)
      
      const result = await getUserCreditSummary()
      if (result.success) {
        setTransactions(result.recentTransactions.slice(0, maxTransactions))
        setError(null)
      }
    } catch (err) {
      console.error('Failed to load credit history:', err)
      setError(err instanceof Error ? err.message : 'Failed to load history')
    } finally {
      setLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [maxTransactions])

  const filteredTransactions = transactions.filter(transaction => {
    if (filter === 'all') return true
    if (filter === 'purchase') return transaction.reason === 'purchase' || transaction.reason === 'bonus' || transaction.reason === 'welcome'
    if (filter === 'spend') return ['resume_analysis', 'job_match', 'resume_improvement'].includes(transaction.reason)
    if (filter === 'refund') return transaction.reason === 'refund'
    return true
  })

  const getTotalByType = (type: TransactionFilter) => {
    return transactions
      .filter(t => {
        if (type === 'purchase') return t.amount > 0
        if (type === 'spend') return t.amount < 0
        return true
      })
      .reduce((sum, t) => sum + Math.abs(t.amount), 0)
  }

  if (loading) {
    return (
      <div className={`bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-gray-600 rounded"></div>
            <div className="h-6 bg-gray-600 rounded w-32"></div>
          </div>
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
    )
  }

  if (error) {
    return (
      <div className={`bg-red-900/20 backdrop-blur-sm p-6 rounded-lg border border-red-700 ${className}`}>
        <div className="flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <div>
            <h3 className="font-medium">{t('history.error.title', { default: 'Failed to load history' })}</h3>
            <p className="text-sm text-red-300">{error}</p>
            <button
              onClick={() => loadTransactions()}
              className="mt-2 text-sm text-red-200 hover:text-red-100 underline"
            >
              {t('history.error.retry', { default: 'Try again' })}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-gray-900/70 backdrop-blur-sm p-6 rounded-lg border border-gray-700 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gray-700/50 rounded-lg">
            <History className="w-6 h-6 text-gray-300" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-100">
              {t('history.title', { default: 'Credit History' })}
            </h3>
            <p className="text-sm text-gray-400">
              {t('history.subtitle', { 
                default: 'Track your credit purchases and usage',
                count: filteredTransactions.length 
              })}
            </p>
          </div>
        </div>
        
        <button
          onClick={() => loadTransactions(true)}
          disabled={isRefreshing}
          className="p-2 text-gray-400 hover:text-gray-200 transition-colors"
          title={t('history.refresh', { default: 'Refresh' })}
        >
          <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={<TrendingUp className="w-4 h-4 text-green-400" />}
          label={t('history.stats.earned', { default: 'Earned' })}
          value={getTotalByType('purchase')}
          positive
        />
        <StatCard
          icon={<TrendingDown className="w-4 h-4 text-red-400" />}
          label={t('history.stats.spent', { default: 'Spent' })}
          value={getTotalByType('spend')}
          positive={false}
        />
        <StatCard
          icon={<CreditCard className="w-4 h-4 text-blue-400" />}
          label={t('history.stats.transactions', { default: 'Transactions' })}
          value={transactions.length}
        />
        <StatCard
          icon={<Calendar className="w-4 h-4 text-purple-400" />}
          label={t('history.stats.this_month', { default: 'This Month' })}
          value={transactions.filter(t => 
            new Date(t.createdAt).getMonth() === new Date().getMonth()
          ).length}
        />
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="flex items-center gap-2 mb-6 overflow-x-auto">
          <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
          {(['all', 'purchase', 'spend', 'refund'] as const).map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                filter === filterType
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {t(`history.filters.${filterType}`, { 
                default: filterType.charAt(0).toUpperCase() + filterType.slice(1) 
              })}
            </button>
          ))}
        </div>
      )}

      {/* Transaction List */}
      {filteredTransactions.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <History className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-lg font-medium">
            {t('history.empty.title', { default: 'No transactions found' })}
          </p>
          <p className="text-sm">
            {filter === 'all' 
              ? t('history.empty.message_all', { default: 'Your credit transactions will appear here' })
              : t('history.empty.message_filtered', { 
                  default: 'No transactions match the selected filter',
                  filter 
                })
            }
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          <AnimatePresence>
            {filteredTransactions.map((transaction, index) => (
              <TransactionItem
                key={transaction.id}
                transaction={transaction}
                locale={locale}
                index={index}
                t={t}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Export Button */}
      {filteredTransactions.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={() => exportTransactions(filteredTransactions, locale)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            <Download className="w-4 h-4" />
            {t('history.export', { default: 'Export History' })}
          </button>
        </div>
      )}
    </div>
  )
}

// Stat card component
function StatCard({ 
  icon, 
  label, 
  value, 
  positive 
}: { 
  icon: React.ReactNode
  label: string
  value: number
  positive?: boolean 
}) {
  return (
    <div className="bg-gray-800/50 p-4 rounded-lg">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-gray-400 font-medium">{label}</span>
      </div>
      <div className={`text-lg font-bold ${
        positive === true ? 'text-green-400' : 
        positive === false ? 'text-red-400' : 'text-gray-100'
      }`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
    </div>
  )
}

// Transaction item component
function TransactionItem({ 
  transaction, 
  locale, 
  index,
  t 
}: { 
  transaction: Transaction
  locale: string
  index: number
  t: any 
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isPositive = transaction.amount > 0
  
  const getReasonIcon = (reason: string) => {
    switch (reason) {
      case 'purchase':
        return <CreditCard className="w-4 h-4 text-green-400" />
      case 'refund':
        return <RefreshCw className="w-4 h-4 text-yellow-400" />
      case 'resume_analysis':
      case 'job_match':
      case 'resume_improvement':
        return <TrendingDown className="w-4 h-4 text-red-400" />
      default:
        return <History className="w-4 h-4 text-gray-400" />
    }
  }

  const getReasonDisplay = (reason: string) => {
    const reasons = {
      purchase: t('reasons.purchase', { default: 'Credit Purchase' }),
      refund: t('reasons.refund', { default: 'Refund' }),
      resume_analysis: t('reasons.resume_analysis', { default: 'Resume Analysis' }),
      job_match: t('reasons.job_match', { default: 'Job Matching' }),
      resume_improvement: t('reasons.resume_improvement', { default: 'Resume Improvement' }),
      welcome: t('reasons.welcome', { default: 'Welcome Bonus' }),
      bonus: t('reasons.bonus', { default: 'Bonus Credits' }),
      manual: t('reasons.manual', { default: 'Manual Adjustment' })
    }
    return reasons[reason as keyof typeof reasons] || reason
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ delay: index * 0.05 }}
      className="bg-gray-800/30 border border-gray-700/50 rounded-lg overflow-hidden"
    >
      <div 
        className="p-4 cursor-pointer hover:bg-gray-700/20 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getReasonIcon(transaction.reason)}
            <div>
              <div className="font-medium text-gray-200">
                {getReasonDisplay(transaction.reason)}
              </div>
              <div className="text-sm text-gray-400">
                {new Date(transaction.createdAt).toLocaleDateString(locale, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <span className={`font-bold ${
              isPositive ? 'text-green-400' : 'text-red-400'
            }`}>
              {isPositive ? '+' : ''}{transaction.amount}
            </span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`} />
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      <AnimatePresence>
        {isExpanded && transaction.metadata && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-gray-700/50 px-4 py-3 bg-gray-800/20"
          >
            <div className="text-sm text-gray-400 space-y-1">
              <div className="font-medium text-gray-300 mb-2">
                {t('history.details', { default: 'Transaction Details' })}
              </div>
              {Object.entries(transaction.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}:</span>
                  <span className="text-gray-300">{String(value)}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Export function
function exportTransactions(transactions: Transaction[], locale: string) {
  const headers = ['Date', 'Type', 'Amount', 'Description']
  const rows = transactions.map(t => [
    new Date(t.createdAt).toLocaleDateString(locale),
    t.reason,
    t.amount.toString(),
    `${t.amount > 0 ? 'Credit' : 'Debit'} transaction`
  ])

  const csvContent = [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `credit-history-${new Date().toISOString().split('T')[0]}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export default CreditHistory
