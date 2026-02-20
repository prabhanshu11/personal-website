# Loki Mode - Working Memory

**Session Start:** 2026-01-11
**Project:** GitHub Habit Tracker Dashboard Enhancement
**Current Phase:** Discovery
**Active Feature:** Iceberg Chart Visualization (Time-Series Activity Graph)

---

## Completion Promise

Implement and deploy Code Activity/Pulse Dashboard with:
1. ✅ Time-series backend endpoint (additions, deletions, commits over time)
2. ✅ Iceberg chart component (bi-directional Y-axis, smooth curves, inverted bars)
3. ✅ Sort toggle for repo cards (Activity/Commits/Recent/A-Z)
4. ✅ Time window filter (1W/1M/1Y/5Y)
5. ✅ Screenshot verification of UI
6. ✅ Test suite (unit + integration)
7. ✅ PR created and merged

**Status:** 0/7 complete | Estimated: 8-12 agent dispatches

---

## Current Context

### What I'm Doing NOW
- Bootstrapping Loki Mode infrastructure
- About to analyze existing codebase structure
- Will create task decomposition for iceberg chart feature

### Project Architecture (Known)
**Backend:** FastAPI (Python) with SQLAlchemy async ORM
- Database: SQLite with async support
- Existing models: Repository, Commit, CommitFile
- Current endpoints: `/metrics/summary`, `/repos/{id}/commits`

**Frontend:** Next.js 16.1.1 with Turbopack
- UI Framework: Tailwind CSS with custom "neo-brutalist" design system
- Data Fetching: SWR (stale-while-revalidate)
- Current features: 48h/24h/7d summary cards, per-repo metrics

### Existing Layout (Must Preserve)
```
Repo Card:
[repo name + badge]  [+850/-395 files]  [1245 lines]  [42 commits]
                                                       [7 l/c]
```

---

## Next Actions (RARV Cycle)

### REASON
1. Read existing backend code to understand data model
2. Read existing frontend code to understand component structure
3. Identify insertion points for new features

### ACT (Planned)
1. Design time-series API endpoint schema
2. Implement backend endpoint with aggregation by time buckets
3. Create React chart component (Recharts library)
4. Add sort toggle state management
5. Add time window filter UI
6. Wire everything together

### REFLECT (After Each Action)
- Run backend tests (`pytest`)
- Start dev servers and verify with curl
- Take screenshots of frontend
- Update this file with progress

### VERIFY
- Backend: API response matches OpenAPI spec
- Frontend: Visual verification via screenshots
- Integration: End-to-end flow test
- Performance: Response time < 500ms for 7d window

---

## Mistakes & Learnings

### Session Learnings
- (Empty - fresh session)

### Anti-Patterns to Avoid
- ❌ Don't implement without testing backend first
- ❌ Don't skip screenshot verification
- ❌ Don't push to git until tests pass locally
- ❌ Don't work on multiple features in parallel

---

## Open Questions / Blockers

- None currently

---

## Recent Changes

- 2026-01-11 00:00 UTC: Session initialized, .loki/ structure created

---

## Episodic Memory Index

- (Will populate as tasks complete)

---

## Git Checkpoint

**Last Known Good State:** main branch HEAD (before Loki Mode changes)
**Current Branch:** Will create `feature/iceberg-dashboard`
