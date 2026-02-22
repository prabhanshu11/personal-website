'use client'

import { useAccounts, formatINR, formatDateTime } from '@/lib/api'

export default function AccountsPage() {
  const { data, error, isLoading } = useAccounts()

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-2 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-surface rounded-lg border border-border p-5 animate-pulse h-32" />
        ))}
      </div>
    )
  }

  if (error) {
    return <div className="text-negative text-center p-8">{error.message}</div>
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-surface rounded-lg border border-border p-8 text-center text-muted">
        No accounts found. Transactions will auto-create accounts as emails are parsed.
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {data.map(acc => (
        <div key={acc.id} className="bg-surface rounded-lg border border-border p-5 hover:border-accent/30 transition">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="font-medium text-ink">{acc.name}</h3>
              <p className="text-xs text-muted">{acc.bank} &middot; {acc.type.replace('_', ' ')}</p>
            </div>
            <BankBadge bank={acc.bank} />
          </div>

          {acc.last_known_balance !== null ? (
            <div className="mb-3">
              <p className="text-2xl font-semibold text-ink">{formatINR(acc.last_known_balance)}</p>
              {acc.balance_updated_at && (
                <p className="text-xs text-muted">as of {formatDateTime(acc.balance_updated_at)}</p>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted mb-3">Balance not available</p>
          )}

          <div className="flex items-center gap-4 text-xs text-muted">
            <span>{acc.transaction_count} transactions</span>
            {acc.identifier && <span>****{acc.identifier}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}

function BankBadge({ bank }: { bank: string }) {
  const colors: Record<string, string> = {
    'HDFC': 'bg-blue-500/20 text-blue-400',
    'IOB': 'bg-green-500/20 text-green-400',
  }
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[bank] || 'bg-accent/10 text-accent'}`}>
      {bank}
    </span>
  )
}
