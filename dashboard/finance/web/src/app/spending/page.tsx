'use client'

import { useMonthlySpending, useCategoryBreakdown, formatINR, categoryLabel } from '@/lib/api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

const PIE_COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4', '#f97316', '#6366f1', '#14b8a6',
]

export default function SpendingPage() {
  const { data: monthly, isLoading: loadingMonthly } = useMonthlySpending(6)
  const { data: categories, isLoading: loadingCats } = useCategoryBreakdown()

  return (
    <div className="space-y-8">
      {/* Monthly trend */}
      <section>
        <h2 className="text-sm font-medium text-muted mb-4">Monthly Spending (6 months)</h2>
        <div className="bg-surface rounded-lg border border-border p-4">
          {loadingMonthly ? (
            <div className="h-64 animate-pulse flex items-center justify-center text-muted">Loading...</div>
          ) : !monthly || monthly.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-muted">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={[...monthly].reverse()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                  labelStyle={{ color: '#f1f5f9' }}
                  formatter={(v: number, name: string) => [formatINR(v), name === 'total_debit' ? 'Spent' : 'Income']}
                />
                <Bar dataKey="total_debit" fill="#ef4444" radius={[4, 4, 0, 0]} name="total_debit" />
                <Bar dataKey="total_credit" fill="#22c55e" radius={[4, 4, 0, 0]} name="total_credit" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>

      {/* Category breakdown (current month) */}
      <section>
        <h2 className="text-sm font-medium text-muted mb-4">This Month by Category</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {/* Pie chart */}
          <div className="bg-surface rounded-lg border border-border p-4">
            {loadingCats ? (
              <div className="h-64 animate-pulse flex items-center justify-center text-muted">Loading...</div>
            ) : !categories || categories.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-muted">No spending data</div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={categories.map(c => ({ name: categoryLabel(c.category), value: c.total }))}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {categories.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                    formatter={(v: number) => formatINR(v)}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: 12, color: '#94a3b8' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Category list */}
          <div className="bg-surface rounded-lg border border-border p-4">
            {!categories || categories.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-muted">No data</div>
            ) : (
              <div className="space-y-3">
                {categories.map((cat, i) => {
                  const total = categories.reduce((s, c) => s + c.total, 0)
                  const pct = total > 0 ? (cat.total / total) * 100 : 0
                  return (
                    <div key={cat.category}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="flex items-center gap-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full inline-block"
                            style={{ background: PIE_COLORS[i % PIE_COLORS.length] }}
                          />
                          {categoryLabel(cat.category)}
                        </span>
                        <span className="text-muted">{formatINR(cat.total)} ({cat.count})</span>
                      </div>
                      <div className="w-full bg-border rounded-full h-1.5">
                        <div
                          className="h-1.5 rounded-full transition-all"
                          style={{ width: `${pct}%`, background: PIE_COLORS[i % PIE_COLORS.length] }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
