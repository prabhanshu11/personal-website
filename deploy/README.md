# Deployment

## How It Works

```
git push origin main
       ↓
GitHub Actions (free VM, ~12 lines YAML)
       ↓
SSH into VPS
       ↓
./deploy/run.sh (all logic here)
```

**Trigger:** `git push` to main branch
**Result:** VPS pulls latest code and rebuilds containers

## Architecture

- **GitHub Actions** = Free VM that SSHs to VPS on push (minimal YAML, no vendor lock-in logic)
- **deploy/run.sh** = All deployment logic (portable, could work with any trigger)
- **VPS** = Runs containers, serves traffic

## Files

| File | Purpose |
|------|---------|
| `run.sh` | Main deployment script (runs on VPS) |
| `setup-vps.sh` | One-time VPS setup |
| `nginx/` | Nginx site configs |
| `systemd/` | Systemd service files |
| `bootstrap_server.md` | Initial server setup notes |
| `../.github/workflows/deploy.yml` | GitHub Actions trigger (just SSH) |

## AI Agents: VPS is READ-ONLY

**DO NOT SSH to VPS for deployment.** All deployments go through git push:

```bash
# CORRECT: Push triggers deployment via GitHub Actions
git push origin main

# WRONG: Never do this
ssh root@... "./deploy/run.sh"  # PROHIBITED
```

See `CLAUDE.md` in project root for full VPS Access Rules.

## Emergency Manual Deployment (Human Only)

If GitHub Actions is completely down and human intervention is needed:

```bash
# ONLY for human operators, NOT AI agents
ssh root@72.60.218.33
cd /var/www/prabhanshu.space
git pull origin main
./deploy/run.sh
```

## Why This Pattern

- All logic in `run.sh` (git-tracked, portable)
- GitHub Actions is just a free trigger mechanism
- Could switch to GitLab CI, webhook, or cron with minimal changes
- No complex YAML DSL - just "SSH and run script"
