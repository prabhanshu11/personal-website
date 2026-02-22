import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Finance Dashboard',
  description: 'Personal financial overview — transactions, spending, accounts',
}

const tabs = [
  { href: '/dashboard/finance', label: 'Overview' },
  { href: '/dashboard/finance/transactions', label: 'Transactions' },
  { href: '/dashboard/finance/spending', label: 'Spending' },
  { href: '/dashboard/finance/accounts', label: 'Accounts' },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          {/* Header */}
          <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-10">
            <div className="max-w-6xl mx-auto px-4 py-3">
              <h1 className="text-lg font-semibold text-ink">Finance</h1>
            </div>
            {/* Tab navigation */}
            <nav className="max-w-6xl mx-auto px-4 flex gap-1">
              {tabs.map(tab => (
                <TabLink key={tab.href} href={tab.href} label={tab.label} />
              ))}
            </nav>
          </header>
          {/* Content */}
          <main className="max-w-6xl mx-auto px-4 py-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

function TabLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="px-4 py-2 text-sm text-muted hover:text-ink transition-colors border-b-2 border-transparent hover:border-accent/50"
    >
      {label}
    </Link>
  )
}


