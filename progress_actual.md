# Project Progress & Roadmap (Private)

## ✅ Completed Phases

### Phase 1-3: Core Infrastructure (Done)
- **VPS Setup**: Server provisioned, Docker installed, Nginx & SSL configured.
- **Base Website**: Portfolio content, "Data Scientist" profile, mobile text fixes.
- **Dev Environment**: Docker-based local development workflow.

### ⚠️ Phase 4: Continuous Deployment (Needs Debugging)
- **Step 4.1: GitHub Actions:** Workflow exists but has a history of failures (needs investigation).
- **Step 4.2: Automation:** Currently relying on manual `deploy` command until CI/CD is fixed.

---

## 🚧 Upcoming Phases: "My Zone"

### Phase 5: Foundation & Auth
- [ ] **Auth**: GitHub Login (Passkey compatible) restricted to `prabhanshu11`.
- [ ] **Mobile**: Landing page must have "Sign in to Newsletter" section.
- [ ] **UI**: Simple header buttons to switch between "Dashboard" and "TV" modes.

### Phase 6: The Dashboard (My Zone)
*Synced via Syncthing where applicable.*

#### 6.1 Financial & Calendar
- [ ] **Financial Planning**: Basic tracking/projection.
- [ ] **Daily Calendar**:
    - [ ] "Time wasted today" tracker.
    - [ ] "Hours/mins remaining" until 12am sleep time.
    - [ ] "Things to do today" (synced from Obsidian vault).

#### 6.2 Long Term & Habits
- [ ] **Life in Weeks**: Grid of small rectangles showing remaining weeks.
- [ ] **Weekly Streaks**:
    - [ ] Calories burnt.
    - [ ] Steps run.
    - [ ] Calories eaten.
    - [ ] Protein eaten.
    - [ ] **Git Pushes**: Count pushes to own repo (leverage `habit-tracker-git-commits` repo).
    - [ ] Ice baths done.
- [ ] **Jerked Off Tracker**:
    - [ ] Mobile notifications asking at random times to fill data.
    - [ ] Manual entry for past days (timesheet style).

#### 6.3 Personal Logs
- [ ] **Sleep/Wake**: Track wake up and sleep times.
- [ ] **Weekly Todo**: High-level weekly goals.
- [ ] **Contextual Routine View**:
    - [ ] **Evening**: Show evening routine.
    - [ ] **Morning**: Show previous day's todo, morning routine, steps, treadmill km.

#### 6.4 Household
- [ ] **Cooking & Dishes**: Dashboard for tracking/assignments.
- [ ] **Laundry & Office**: Laundry days vs. Office days tracking.

### Phase 7: TV Mode & Media
- [ ] **Connectivity**: Connects to NAS.
- [ ] **Streaming**: Stream pre-downloaded videos via internet or tunnel (when on same WiFi/Hotspot).
- [ ] **Display**:
    - [ ] Default style: Slideshow of dashboards.
    - [ ] Show TV at specific hours or via Telegram bot request.

### Phase 8: Advanced Integrations
- [ ] **Spotify**: Integrate `Programs/dont-drop-my-songs`.
    - [ ] Action: Start with `Programs/dont-drop-my-songs/replit_downloaded_working_project/TODO.md`.
- [ ] **Image Recognition (Backend)**:
    - [ ] Hardware: TP-Link WiFi Camera.
    - [ ] Goal: Identify dashboard metrics automatically.
    - [ ] Robotics: Develop chain of control/sensor to move camera and track items/activities.

---

## 📝 Notes
- **Mobile First**: Both Landing Page and My Zone must be fully mobile-responsive.
- **Privacy**: This file (`progress_actual.md`) is gitignored.
