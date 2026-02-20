"use client"

import { ResponsiveContainer, ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, ReferenceLine, CartesianGrid } from 'recharts'
import { useState, useEffect, useMemo } from 'react'

// Generate consistent colors for repos using HSL golden ratio spacing
function getRepoColor(repoName: string, index: number): string {
  const goldenRatio = 0.618033988749895
  const hue = (index * goldenRatio * 360) % 360
  return `hsl(${hue}, 65%, 55%)`
}

type RepoCommitActivity = {
  repo_id: number
  repo_name: string
  count: number
  total_lines: number
}

type TimeSeriesDataPoint = {
  timestamp: string
  additions: number
  deletions: number
  total_activity: number
  commits_by_repo: RepoCommitActivity[]
}

type IcebergChartProps = {
  data: TimeSeriesDataPoint[]
  className?: string
}

export function IcebergChart({ data, className = '' }: IcebergChartProps) {
  // Transform data for Recharts format
  const chartData = useMemo(() => {
    return data.map(point => {
      // Create an object with additions, deletions, total_activity
      // and negative values for commits (to create inverted bars)
      const repoCommits: Record<string, number> = {}
      let totalCommits = 0

      point.commits_by_repo.forEach(repo => {
        // Use negative values for inverted bar chart
        repoCommits[repo.repo_name] = -repo.count
        totalCommits += repo.count
      })

      return {
        // Format timestamp for display
        time: new Date(point.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        additions: point.additions,
        deletions: point.deletions,
        total_activity: point.total_activity,
        total_commits: -totalCommits, // Negative for inverted display
        ...repoCommits
      }
    })
  }, [data])

  // Extract unique repo names for stacking
  const repoNames = useMemo(() => {
    const names = new Set<string>()
    data.forEach(point => {
      point.commits_by_repo.forEach(repo => {
        names.add(repo.repo_name)
      })
    })
    return Array.from(names)
  }, [data])

  // Generate repo color map
  const repoColors = useMemo(() => {
    const colors: Record<string, string> = {}
    repoNames.forEach((name, index) => {
      colors[name] = getRepoColor(name, index)
    })
    return colors
  }, [repoNames])

  // Calculate Y-axis domain (max positive for lines, max negative for bars)
  const [yDomain, setYDomain] = useState<[number, number]>([0, 0])

  useEffect(() => {
    if (chartData.length === 0) {
      setYDomain([-10, 10])
      return
    }

    const maxActivity = Math.max(...chartData.map(d => d.total_activity || 0))
    const minCommits = Math.min(...chartData.map(d => d.total_commits || 0))

    // Add 10% padding
    const upperBound = maxActivity * 1.1
    const lowerBound = minCommits * 1.1

    setYDomain([lowerBound, upperBound])
  }, [chartData])

  if (chartData.length === 0) {
    return (
      <div className={`ink-panel p-8 text-center ${className}`}>
        <div className="text-sm opacity-60">No activity data available for this time window</div>
      </div>
    )
  }

  return (
    <div className={`ink-panel p-6 ${className}`}>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--ink)" opacity={0.1} />

          <XAxis
            dataKey="time"
            stroke="var(--ink)"
            style={{ fontSize: '12px', fontFamily: 'ui-monospace, monospace' }}
          />

          <YAxis
            stroke="var(--ink)"
            style={{ fontSize: '12px', fontFamily: 'ui-monospace, monospace' }}
            domain={yDomain}
          />

          <Tooltip
            contentStyle={{
              background: 'var(--panel)',
              border: '2px solid var(--ink)',
              borderRadius: '8px',
              boxShadow: '0 2px 0 var(--ink)',
              fontFamily: 'ui-sans-serif, system-ui',
              fontSize: '12px'
            }}
          />

          {/* Zero line divider */}
          <ReferenceLine y={0} stroke="var(--ink)" strokeWidth={2} />

          {/* Upper hemisphere - Lines for code volume */}
          <Line
            type="monotone"
            dataKey="total_activity"
            stroke="var(--ink)"
            strokeWidth={3}
            dot={false}
            name="Total Activity"
          />
          <Line
            type="monotone"
            dataKey="additions"
            stroke="#2E7D32"
            strokeWidth={2}
            dot={false}
            name="Additions"
          />
          <Line
            type="monotone"
            dataKey="deletions"
            stroke="#D84315"
            strokeWidth={2}
            dot={false}
            name="Deletions"
          />

          {/* Lower hemisphere - Inverted stacked bars for commits */}
          {repoNames.map((repoName, index) => (
            <Bar
              key={repoName}
              dataKey={repoName}
              stackId="commits"
              fill={repoColors[repoName]}
              opacity={0.8}
              name={repoName}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-[var(--ink)]" style={{ height: '3px' }} />
          <span>Total Activity</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5" style={{ height: '2px', backgroundColor: '#2E7D32' }} />
          <span className="additions-color">Additions</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5" style={{ height: '2px', backgroundColor: '#D84315' }} />
          <span className="deletions-color">Deletions</span>
        </div>
        <div className="ml-4 opacity-60">|</div>
        <div className="ml-2 opacity-60 text-[10px]">Commits (inverted bars below)</div>
      </div>
    </div>
  )
}
