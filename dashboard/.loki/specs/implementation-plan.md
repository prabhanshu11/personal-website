# Iceberg Dashboard - Senior SWE Implementation Plan

**Confidence Level:** HIGH ✓
**Complexity:** Moderate (4/10)
**Estimated Agent Dispatches:** 6-8 (parallelizable)
**Risk Level:** Low (additive feature, no breaking changes)

---

## Architecture Analysis

### Existing Foundation (Verified)
✅ **Backend:** FastAPI with async SQLAlchemy - ready for time-series aggregation
✅ **Frontend:** Next.js + SWR - ready for chart library integration
✅ **Data Model:** Commit table has `committed_at`, `additions`, `deletions` - sufficient
✅ **UI System:** Custom CSS variables + Tailwind - consistent styling available

### New Components Required
1. Backend: `GET /metrics/timeseries` endpoint
2. Frontend: `IcebergChart` component (Recharts)
3. Frontend: `SortToggle` component
4. Frontend: `TimeWindowFilter` component

---

## Implementation Strategy

### Phase 1: Backend Time-Series Endpoint (30 min)

**File:** `dashboard/habit-tracker/backend/src/habits_api/app.py`

**Endpoint Spec:**
```python
GET /metrics/timeseries?window=1M&granularity=day
Response: {
  "window": "1M",
  "granularity": "day",
  "data_points": [
    {
      "timestamp": "2026-01-10T00:00:00Z",
      "additions": 850,
      "deletions": 395,
      "total_activity": 1245,
      "commits_by_repo": {
        "prabhanshu11/repo1": {"count": 5, "total_lines": 423},
        "prabhanshu11/repo2": {"count": 3, "total_lines": 122}
      }
    },
    ...
  ]
}
```

**Implementation:**
- Use SQLAlchemy `func.date_trunc()` for time bucketing
- Join Commit table, group by time bucket + repo_id
- Return max 100 data points (to prevent response bloat)
- Optimize with indexes on `committed_at` column (already indexed ✓)

**Testing:**
- Unit test: Verify correct time bucket aggregation
- Integration test: Curl endpoint, verify JSON shape
- Performance test: 1Y window should return in < 500ms

---

### Phase 2: Iceberg Chart Component (45 min)

**File:** `dashboard/habit-tracker/web/src/components/IcebergChart.tsx`

**Library Choice:** Recharts (already has smooth curves, composable charts, good TypeScript support)

**Component Structure:**
```tsx
<ResponsiveContainer width="100%" height={400}>
  <ComposedChart data={timeSeriesData}>
    {/* Upper hemisphere - Lines */}
    <Line type="monotone" dataKey="total_activity" stroke="#121212" strokeWidth={3} />
    <Line type="monotone" dataKey="additions" stroke="#2E7D32" strokeWidth={2} />
    <Line type="monotone" dataKey="deletions" stroke="#D84315" strokeWidth={2} />

    {/* Zero line */}
    <ReferenceLine y={0} stroke="#121212" strokeWidth={2} />

    {/* Lower hemisphere - Inverted bars */}
    <Bar dataKey="commits" stackId="a" fill={repoColorMap} />
  </ComposedChart>
</ResponsiveContainer>
```

**Key Features:**
- Smooth curves with `type="monotone"` (Recharts built-in)
- Bi-directional Y-axis: positive for lines, negative for commits
- Opacity based on lines changed: Use `fillOpacity` calculated per commit
- Repo color persistence: Generate HSL colors, store in localStorage

**Styling:** Match existing neo-brutalist theme (border: 2px solid, box-shadow)

**Testing:**
- Screenshot verification with sample data
- Test edge cases (no data, single data point, 100+ repos)

---

### Phase 3: Sort Toggle Component (15 min)

**File:** `dashboard/habit-tracker/web/src/components/SortToggle.tsx`

**UI Spec:**
```tsx
<button className="pill" onClick={cycleSort}>
  {sortLabel} ↓
</button>
```

**State Management:**
- Local state: `const [sortMode, setSortMode] = useState<'activity' | 'commits' | 'recent' | 'az'>('activity')`
- Cycle through modes on click
- Apply sort to `per_repo` array before rendering

**Sorting Logic:**
- Activity: `(a + d)` desc
- Commits: `commits_count` desc
- Recent: Parse `last_checked_at`, newest first
- A-Z: `full_name` alphabetical

**Testing:**
- Screenshot each sort mode
- Verify correct order with known data

---

### Phase 4: Time Window Filter (15 min)

**File:** `dashboard/habit-tracker/web/src/components/TimeWindowFilter.tsx`

**UI Spec:**
```tsx
<div className="flex gap-2">
  {['1W', '1M', '1Y', '5Y'].map(w => (
    <button
      key={w}
      className={`pill ${activeWindow === w ? 'bg-accent' : ''}`}
      onClick={() => setWindow(w)}
    >
      {w}
    </button>
  ))}
</div>
```

**Integration:**
- Update SWR key when window changes: `useSWR(\`/metrics/timeseries?window=${window}\`)`
- Chart auto-updates via SWR revalidation

**Testing:**
- Click each filter, verify API call with correct window param
- Screenshot each time window to verify data changes

---

### Phase 5: Integration & Polish (30 min)

**Files to Update:**
- `dashboard/habit-tracker/web/src/app/page.tsx` - Add chart section above repo cards
- `dashboard/habit-tracker/web/src/app/globals.css` - Add chart-specific styles if needed

**Integration Points:**
1. Fetch time-series data with SWR (parallel to existing summary fetches)
2. Place chart between summary cards and repo list
3. Wire sort toggle to repo card rendering
4. Wire time filter to both chart and summary cards

**Error Handling:**
- Loading state: Show skeleton loader for chart
- Error state: Show error message, allow retry
- Empty state: "No activity in selected time window"

**Testing:**
- Full E2E flow: Change window → verify chart updates → change sort → verify cards reorder
- Screenshot verification at each step
- Check responsive layout (mobile, tablet, desktop)

---

### Phase 6: Test Suite & PR (30 min)

**Backend Tests:**
```bash
cd dashboard/habit-tracker/backend
pytest tests/ -v
```

**New Tests to Add:**
- `test_timeseries_endpoint_24h.py`
- `test_timeseries_endpoint_1M.py`
- `test_timeseries_granularity.py`

**Frontend Tests:**
- None required (visual verification via screenshots sufficient for UI)

**Git Flow:**
```bash
git checkout -b feature/iceberg-dashboard
git add .
git commit -m "feat: add iceberg chart visualization with time-series API

- Implement /metrics/timeseries endpoint with time bucketing
- Add IcebergChart component with Recharts (smooth curves + inverted bars)
- Add SortToggle for repo cards (Activity/Commits/Recent/A-Z)
- Add TimeWindowFilter (1W/1M/1Y/5Y)
- Maintain existing neo-brutalist design system
- All tests passing

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push -u origin feature/iceberg-dashboard
gh pr create --title "Iceberg Dashboard Visualization" --body "..."
```

**Merge Criteria:**
- ✅ All backend tests pass
- ✅ Backend dev server starts without errors
- ✅ Frontend builds without errors (`npm run build`)
- ✅ Screenshot verification shows correct UI
- ✅ Manual test: Change filters, verify updates

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Recharts bundle size | Low | Already using React, incremental cost acceptable |
| Time-series query slow | Low | Indexed `committed_at`, limit to 100 points |
| Chart rendering lag | Low | Recharts optimized, max 100 data points |
| Color collision (repos) | Low | Use HSL with golden ratio spacing |
| Breaking existing UI | Very Low | Additive feature, no modifications to current cards |

---

## Confidence Statement

**As a Senior SWE, I am confident this plan will succeed because:**

1. ✅ Existing codebase has all necessary data (Commit model with timestamps)
2. ✅ Architecture supports new endpoint (FastAPI async, already has similar aggregation in `/metrics/summary`)
3. ✅ Frontend framework ready (Next.js + SWR pattern established)
4. ✅ Design system consistent (CSS variables + Tailwind utilities available)
5. ✅ No breaking changes (purely additive feature)
6. ✅ Clear testing strategy (backend unit tests + frontend screenshots)
7. ✅ Scope well-defined (user spec is precise, no ambiguity)

**Estimated Timeline:** 2-3 hours of focused work (parallelizable to 6-8 agents)

**Failure Modes:** None anticipated (low complexity, well-understood problem space)

---

## Agent Dispatch Plan

### Parallel Track 1: Backend (Sonnet)
1. Implement `/metrics/timeseries` endpoint
2. Write backend unit tests
3. Verify with curl

### Parallel Track 2: Frontend - Chart (Sonnet)
1. Install Recharts dependency
2. Implement IcebergChart component
3. Wire to API with SWR

### Parallel Track 3: Frontend - Controls (Haiku, parallel)
1. Implement SortToggle component
2. Implement TimeWindowFilter component
3. Wire to page.tsx state

### Sequential Track: Integration & Verification (Sonnet)
1. Integrate all components into page.tsx
2. Take screenshots at each step
3. Run full test suite
4. Create PR and merge

**Total Agents:** 6 (2 Sonnet + 4 Haiku, 3 parallel + 1 sequential)

---

## Ready to Execute

**Plan Status:** ✅ COMPLETE
**Confidence:** ✅ HIGH
**Next Action:** Begin autonomous execution with backend implementation

**Senior SWE Signoff:** This plan is production-ready. Proceeding with implementation.

---

*Plan created: 2026-01-11 | Loki Mode v2.35.0*
