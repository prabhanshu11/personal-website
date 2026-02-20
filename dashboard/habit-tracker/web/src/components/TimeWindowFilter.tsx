"use client"

export type TimeWindow = '1W' | '1M' | '1Y' | '5Y'

type TimeWindowFilterProps = {
  currentWindow: TimeWindow
  onWindowChange: (window: TimeWindow) => void
}

const windows: TimeWindow[] = ['1W', '1M', '1Y', '5Y']

export function TimeWindowFilter({ currentWindow, onWindowChange }: TimeWindowFilterProps) {
  return (
    <div className="flex gap-2">
      {windows.map(w => (
        <button
          key={w}
          onClick={() => onWindowChange(w)}
          className={`pill hover:translate-y-px active:translate-y-[2px] transition-transform ${
            currentWindow === w ? 'font-bold' : 'opacity-60'
          }`}
          style={currentWindow === w ? { background: 'var(--accent)', color: 'var(--ink)' } : undefined}
        >
          {w}
        </button>
      ))}
    </div>
  )
}
