'use client'

import { useState } from 'react'
import { useTransactions, formatINR, formatDateTime, categoryLabel, type Transaction } from '@/lib/api'

const CATEGORIES = [
  '', 'food_delivery', 'groceries', 'shopping', 'transfer', 'atm_withdrawal',
  'salary', 'credit_card_spend', 'credit_card_payment', 'emi', 'uncategorized',
]

const TYPES = ['', 'debit', 'credit']

export default function TransactionsPage() {
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [type, setType] = useState('')
  const perPage = 50

  const { data, error, isLoading } = useTransactions(page, perPage, category || undefined, type || undefined)

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <select
          value={category}
          onChange={e => { setCategory(e.target.value); setPage(1) }}
          className="bg-surface border border-border text-sm rounded-md px-3 py-1.5 text-ink focus:outline-none focus:ring-1 focus:ring-accent"
        >
          <option value="">All Categories</option>
          {CATEGORIES.filter(c => c).map(c => (
            <option key={c} value={c}>{categoryLabel(c)}</option>
          ))}
        </select>

        <select
          value={type}
          onChange={e => { setType(e.target.value); setPage(1) }}
          className="bg-surface border border-border text-sm rounded-md px-3 py-1.5 text-ink focus:outline-none focus:ring-1 focus:ring-accent"
        >
          <option value="">All Types</option>
          <option value="debit">Debit</option>
          <option value="credit">Credit</option>
        </select>

        <span className="text-xs text-muted ml-auto">
          Page {page} {data && data.length < perPage && '(last page)'}
        </span>
      </div>

      {/* Table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-muted animate-pulse">Loading...</div>
        ) : error ? (
          <div className="p-8 text-center text-negative">{error.message}</div>
        ) : !data || data.length === 0 ? (
          <div className="p-8 text-center text-muted">No transactions found.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted border-b border-border">
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Merchant</th>
                <th className="px-4 py-2">Category</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.map((txn: Transaction) => (
                <tr key={txn.id} className="border-b border-border/50 hover:bg-surface-hover transition-colors">
                  <td className="px-4 py-2.5 text-muted whitespace-nowrap">{formatDateTime(txn.date)}</td>
                  <td className="px-4 py-2.5">{txn.merchant || '—'}</td>
                  <td className="px-4 py-2.5">
                    <span className="px-2 py-0.5 rounded-full text-xs bg-accent/10 text-accent">
                      {categoryLabel(txn.category)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs font-medium ${txn.type === 'debit' ? 'text-negative' : 'text-positive'}`}>
                      {txn.type.toUpperCase()}
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

      {/* Pagination */}
      <div className="flex gap-2 justify-center">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-3 py-1.5 rounded bg-surface border border-border text-sm hover:bg-surface-hover disabled:opacity-30 transition"
        >
          Previous
        </button>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={data !== undefined && data.length < perPage}
          className="px-3 py-1.5 rounded bg-surface border border-border text-sm hover:bg-surface-hover disabled:opacity-30 transition"
        >
          Next
        </button>
      </div>
    </div>
  )
}
