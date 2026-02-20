"use client"

import { useState } from 'react'

export type SortMode = 'activity' | 'commits' | 'recent' | 'az'

type SortToggleProps = {
  currentSort: SortMode
  onSortChange: (mode: SortMode) => void
}

const sortLabels: Record<SortMode, string> = {
  activity: 'Activity',
  commits: 'Commits',
  recent: 'Recent',
  az: 'A-Z'
}

const sortOrder: SortMode[] = ['activity', 'commits', 'recent', 'az']

export function SortToggle({ currentSort, onSortChange }: SortToggleProps) {
  function cycleSort() {
    const currentIndex = sortOrder.indexOf(currentSort)
    const nextIndex = (currentIndex + 1) % sortOrder.length
    onSortChange(sortOrder[nextIndex])
  }

  return (
    <button
      onClick={cycleSort}
      className="pill hover:translate-y-px active:translate-y-[2px] transition-transform"
      title="Click to change sort order"
    >
      {sortLabels[currentSort]} ↓
    </button>
  )
}
