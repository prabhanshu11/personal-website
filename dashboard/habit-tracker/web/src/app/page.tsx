"use client"

import useSWR from 'swr'
import { useEffect, useMemo, useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/dashboard/api'
const fetcher = (url: string) => fetch(url, { cache: 'no-store' }).then(r => r.json())

type Summary = {
  window: string
  total_commits: number
  total_lines_updated: number
  repos_updated_count: number
  last_checked_at: string | null
  per_repo: { id: number, full_name: string, commits_count: number, is_private: boolean }[]
}

export default function HomePage() {
  const summaryUrl = `${API_BASE}/metrics/summary?window=24h`
  const { data, error, isLoading, mutate } = useSWR<Summary>(summaryUrl, fetcher, { refreshInterval: 15000 })
  const [refreshing, setRefreshing] = useState(false)
  const [showProgress, setShowProgress] = useState(true)
  const [showTape, setShowTape] = useState(true)
  const initializing = isLoading && !data
  const [overlayHide, setOverlayHide] = useState(false)
  const [tapeVariant, setTapeVariant] = useState<'green'|'amber'|'red'|'mint'>('green')
  const [tapeText, setTapeText] = useState<string>('$ habits summary --window=24h')
  const [tapeColored, setTapeColored] = useState(false)
  const [tapeBase, setTapeBase] = useState<string>('$ habits summary --window=24h')
  const [tick, setTick] = useState(0)
  useTapeTicker(showTape, setTick, setTapeText, tapeBase, tapeColored)
  useTapeTicker(initializing && !overlayHide, null, setTapeText, tapeBase, tapeColored)

  async function refreshNow() {
    try {
      setRefreshing(true)
      setShowProgress(true)
      setShowTape(true)
      setTapeColored(false)
      setTapeVariant('amber')
      setTapeBase("$ curl -X POST 'http://127.0.0.1:8081/admin/ingest' && curl 'http://127.0.0.1:8081/metrics/summary?window=24h'")
      setTapeText("$ curl -X POST 'http://127.0.0.1:8081/admin/ingest' && curl 'http://127.0.0.1:8081/metrics/summary?window=24h'")
      await fetch(`${API_BASE}/admin/ingest`, { method: 'POST' })
      // revalidate summary after triggering
      await mutate()
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    if (isLoading && !refreshing) {
      setShowProgress(true)
      setShowTape(true)
      setTapeColored(false)
      setTapeVariant('green')
      setTapeBase("$ curl 'http://127.0.0.1:8081/metrics/summary?window=24h'")
      setTapeText("$ curl 'http://127.0.0.1:8081/metrics/summary?window=24h'")
    }
  }, [isLoading, refreshing])

  useEffect(() => {
    if (data && !isLoading) {
      setTapeVariant('green')
      setTapeBase(`$ ok lines=${data.total_lines_updated} repos=${data.repos_updated_count} window=${data.window}`)
      setTapeText(`$ ok lines=${data.total_lines_updated} repos=${data.repos_updated_count} window=${data.window}`)
      // On initial load, keep text black (not colored). On refresh flows, colorize.
      const c = setTimeout(() => {
        if (refreshing) setTapeColored(true)
      }, 50)
      const p = setTimeout(() => setShowProgress(false), 400)
      const h = setTimeout(() => setShowTape(false), 4000)
      const o = setTimeout(() => setOverlayHide(true), 400)
      return () => { clearTimeout(c); clearTimeout(p); clearTimeout(h); clearTimeout(o) }
    }
  }, [data, isLoading, refreshing])

  return (
    <>
      {/* Initial black overlay with the same tape position */}
      {initializing && (
        <div className={`overlay-screen ${overlayHide ? 'hidden' : ''}`}>
          <div className="max-w-5xl mx-auto px-4" style={{paddingTop: 16}}>
            <div className={`log-tape-v ${tapeVariant} ${tapeColored ? 'colored' : ''}`} aria-live="polite">
              <div className="tape-viewport">
                <div className="tape-col" style={{animationDuration: '4s', animationIterationCount: 1 as any}}>
                  <div className="tape-line">{tapeText}</div>
                  <div className="tape-line" aria-hidden>{tapeText}</div>
                  <div className="tape-line" aria-hidden>{tapeText}</div>
                </div>
              </div>
              <div className="tape-fade-v" />
            </div>
          </div>
        </div>
      )}
      <main className="max-w-5xl mx-auto space-y-6">
      <header className="ink-panel p-6 flex items-center justify-between gap-4 relative">
        <div>
          <h1 className="text-3xl font-bold mb-1">Git Habit Tracker</h1>
          <p className="opacity-80">Activity in the last 24 hours</p>
        </div>
        <div className="hidden md:block flex-1 px-4">
          {showTape && (
          <div className={`log-tape-v transparent ${tapeVariant} ${tapeColored ? 'colored' : ''}`} aria-live="polite">
            <div className="tape-viewport">
              <div className="tape-col" style={{animationDuration: '4s', animationIterationCount: 1 as any}}>
                <div className="tape-line">{tapeText}</div>
                <div className="tape-line" aria-hidden>{tapeText}</div>
                <div className="tape-line" aria-hidden>{tapeText}</div>
              </div>
            </div>
            <div className="tape-fade-v" />
          </div>
          )}
        </div>
        <button onClick={refreshNow} disabled={refreshing} className="pill hover:translate-y-px active:translate-y-[2px] transition-transform">
          {refreshing ? 'Refreshing…' : 'Refresh now'}
        </button>
        {showProgress && (
          <div className="absolute -bottom-3 left-4 right-4">
            <div className="progress-retro">
              <div className="progress-fill" />
            </div>
          </div>
        )}
      </header>

      <section className="ink-panel p-6 flex items-center justify-between">
        <div>
          <div className="text-sm opacity-80">Lines updated (24h)</div>
          <div className="big-number font-extrabold">{isLoading ? '…' : (data?.total_lines_updated ?? 0)}</div>
        </div>
        <div className="text-right space-y-1">
          <div>
            <div className="text-sm opacity-80">Repos updated</div>
            <div className="text-lg font-semibold">{isLoading ? '…' : (data?.repos_updated_count ?? 0)}</div>
          </div>
          <div className="text-xs opacity-80">Last checked: {data?.last_checked_at ? new Date(data.last_checked_at).toLocaleString() : '—'}</div>
        </div>
      </section>

      <section className="grid md:grid-cols-2 gap-4">
        {data?.per_repo?.map(r => (
          <a key={r.id} href={`/repo/${r.id}`} className="ink-panel p-4 block hover:-translate-y-0.5 transition-transform">
            <div className="flex items-center justify-between">
              <div className="font-semibold flex items-center gap-2">
                <span>{r.full_name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full border border-black/70" style={{borderWidth:2, background:'white'}}>
                  {r.is_private ? 'private' : 'public'}
                </span>
              </div>
              <div className="text-lg">{r.commits_count}</div>
            </div>
          </a>
        ))}
      </section>
      {error && <div className="text-red-700">Error loading data</div>}
    </main>
    </>
  )
}

// animate dots in the tape during in-flight states
function useTapeTicker(enabled: boolean, setTick: React.Dispatch<React.SetStateAction<number>> | null, setText: (s: string) => void, base: string, colored: boolean) {
  useEffect(() => {
    if (!enabled || colored) return
    let tick = 0
    const id = setInterval(() => {
      tick = (tick + 1) % 12
      const dots = '.'.repeat(tick % 4)
      setText(`${base} ${dots}`)
      if (setTick) setTick(tick)
    }, 250)
    return () => clearInterval(id)
  }, [enabled, colored, base, setTick, setText])
}
