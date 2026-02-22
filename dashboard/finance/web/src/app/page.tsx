'use client'

import { useOverview, useSyncStatus, formatINR, formatDateTime, categoryLabel, triggerSync } from '@/lib/api'
import { useState } from 'react'

export default function OverviewPage() {
  const { data, error, isLoading, mutate } = useOverview()
  const { data: sync } = useSyncStatus()
  const [syncing, setSyncing] = useState(false)

  async function handleSync() {
    setSyncing(true)
    try {
      await triggerSync()
      mutate()
    } catch (e) {
      console.error('Sync failed:', e)
    } finally {
      setSyncing(false)
    }
  }

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState message={error.message} />
  if (!data) return null

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          label="Month Spending"
          value={formatINR(data.month_debit)}
          color="text-negative"
        />
        <SummaryCard
          label="Month Income"
          value={formatINR(data.month_credit)}
          color="text-positive"
        />
        <SummaryCard
          label="Net"
          value={formatINR(data.month_credit - data.month_debit)}
          color={data.month_credit >= data.month_debit ? 'text-positive' : 'text-negative'}
        />
        <SummaryCard
          label="Transactions"
          value={String(data.total_transactions)}
          color="text-accent-light"
          sub={`${data.total_accounts} accounts`}
        />
      </div>

      {/* Sync status */}
      <div className="flex items-center gap-3 text-xs text-muted">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-3 py-1.5 rounded bg-accent/10 text-accent hover:bg-accent/20 transition disabled:opacity-50"
        >
          {syncing ? 'Syncing...' : 'Sync Gmail'}
        </button>
        {sync?.last_sync && (
          <span>Last sync: {formatDateTime(sync.last_sync)} ({sync.emails_processed} emails processed)</span>
        )}
      </div>

      {/* Recent transactions */}
      <section>
        <h2 className="text-sm font-medium text-muted mb-3">Recent Transactions</h2>
        <div className="bg-surface rounded-lg border border-border overflow-hidden">
          {data.recent_transactions.length === 0 ? (
            <div className="p-8 text-center text-muted">
              No transactions yet. Connect Gmail to start parsing.
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-muted border-b border-border">
                  <th className="px-4 py-2">Date</th>
                  <th className="px-4 py-2">Merchant</th>
                  <th className="px-4 py-2">Category</th>
                  <th className="px-4 py-2 text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_transactions.map(txn => (
                  <tr key={txn.id} className="border-b border-border/50 hover:bg-surface-hover transition-colors">
                    <td className="px-4 py-2.5 text-muted">{formatDateTime(txn.date)}</td>
                    <td className="px-4 py-2.5">{txn.merchant || '—'}</td>
                    <td className="px-4 py-2.5">
                      <span className="px-2 py-0.5 rounded-full text-xs bg-accent/10 text-accent">
                        {categoryLabel(txn.category)}
                      </span>
                    </td>
                    <td className={`px-4 py-2.5 text-right font-mono ${txn.type === 'debit' ? 'text-negative' : 'text-positive'}`}>
                      {txn.type === 'debit' ? '−' : '+'}{formatINR(txn.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  )
}

function SummaryCard({ label, value, color, sub }: { label: string; value: string; color: string; sub?: string }) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <p className="text-xs text-muted mb-1">{label}</p>
      <p className={`text-xl font-semibold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-muted mt-1">{sub}</p>}
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-surface rounded-lg border border-border p-4 animate-pulse">
            <div className="h-3 bg-border rounded w-20 mb-2" />
            <div className="h-6 bg-border rounded w-28" />
          </div>
        ))}
      </div>
      <div className="bg-surface rounded-lg border border-border p-4 animate-pulse h-64" />
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="bg-negative/10 border border-negative/20 rounded-lg p-6 text-center">
      <p className="text-negative font-medium">Failed to load dashboard</p>
      <p className="text-sm text-muted mt-1">{message}</p>
    </div>
  )
}
