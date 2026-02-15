# Personal Website - AI Agent Context

## Project Overview
- **Domain**: prabhanshu.space
- **Purpose**: Personal website with blog, projects, and dashboard features
- **Owner**: Prabhanshu Rajpoot (prabhanshu11)

## Architecture

### Components
| Component | URL | Technology | Port |
|-----------|-----|------------|------|
| Main Site | https://prabhanshu.space/ | FastHTML (Docker) | 8000 |
| Habit Tracker | https://prabhanshu.space/dashboard/* | Next.js + FastAPI | 5173/8081 |
| VM Monitor | https://prabhanshu.space/dashboard/vm-monitor/* | FastAPI | 8082 |
| Admin Dashboard | https://prabhanshu.space/myzone/admin | FastHTML (main app) | 8000 |

### Directory Structure on VPS
```
/var/www/personal-website/
├── app.py              # Flask main app
├── templates/          # Jinja2 templates
├── static/             # Static assets
├── dashboard/          # Dashboard services (Docker Compose)
│   ├── habit-tracker/
│   │   ├── web/        # Next.js frontend
│   │   └── backend/    # FastAPI backend
│   ├── vm-monitor/     # VM uptime monitor (FastAPI + SQLite)
│   └── docker-compose.yml
├── deploy/             # Deployment scripts
│   ├── run.sh          # Main deployment script
│   └── nginx/          # nginx configs
├── data/               # SQLite database, persistent data
└── logs/               # Application logs
```

## Shared VPS Infrastructure

### Same VPS (72.60.218.33)
This site shares the VPS with **avantiterraform.com**:

| Site | Domain | Nginx Config |
|------|--------|--------------|
| personal-website | prabhanshu.space | `/etc/nginx/sites-enabled/prabhanshu.space.conf` |
| avantiterraform | avantiterraform.com | `/etc/nginx/sites-enabled/avantiterraform.conf` |

### Unified Deploy Key
Both repos use the SAME SSH deploy key for GitHub Actions:
- **Fingerprint**: `SHA256:0/FaydVfteN4xqu70OdgGli3R54JiLvFECM4SIn4/Kg`
- **Storage**: `pass show github/vps-deploy-key`
- **Setup script**: `vps_bootstrap/scripts/setup-deploy-keys.sh`

### Multi-Site SSL Warning
**Critical**: If one site loses SSL config, it affects the other!
- nginx with only one SSL-enabled server block serves that site for ALL HTTPS
- Always ensure both sites have proper SSL after any deployment
- See avantiterraform incident (Jan 2026) for details

## Deployment

### CI/CD Pipeline
- **Trigger**: Push to `main` branch or manual dispatch
- **Workflow**: `.github/workflows/deploy.yml`
- **Method**: SSH to VPS, run `deploy/run.sh`

### Critical Pattern
Like avantiterraform, use `git fetch + reset --hard` to handle certbot SSL changes:
```bash
git fetch origin main
git reset --hard origin/main
```

## Related Repositories

### Same Owner
- **avantiterraform** - Business website (same VPS)
- **vps_bootstrap** - VPS setup and maintenance scripts
- **local-bootstrapping** - Machine setup, dotfiles (desktop/laptop)

### Important Cross-Repo Awareness
When making changes that affect:
- **nginx config**: Check impact on avantiterraform.com
- **SSL/certbot**: Ensure both sites get SSL reinstalled
- **VPS resources**: Consider Docker container memory usage across both sites

## VPS Access Rules

**READ-ONLY ONLY** - All changes must go through GitHub:
- Allowed: `cat`, `grep`, `ls`, `docker logs`, `systemctl status`
- PROHIBITED: `sudo cp`, `systemctl reload`, `docker run`, file modifications

## Dashboard (Habit Tracker)

### Architecture
- **Frontend**: Next.js at /dashboard/habit-tracker
- **Backend**: FastAPI with SQLite
- **Docker**: Separate containers for web and backend

### Metrics
- 48h default view with 24h subtext
- 7d metrics view available
- Git commit integration for habit tracking

## Admin Dashboard

### Access Control
- Route: `/myzone/admin` — gated by `auth.is_admin(session)`
- Only `prabhanshu11` (ALLOWED_USER) can access
- Non-admin authenticated users get 403
- `is_admin()` is separate from `check_auth()` — when multi-user auth lands, `check_auth()` will allow any user, `is_admin()` stays owner-only

### VM Uptime Monitor
- **Service**: `dashboard/vm-monitor/monitor.py` (FastAPI)
- **Port**: 8082 (host network mode in Docker)
- **Nginx**: `/dashboard/vm-monitor/` proxies to `localhost:8082`
- **Checks**: Tailscale ping (VM up?) + HTTP probe on `:9006` (noVNC tunnel up?)
- **Storage**: SQLite in Docker volume `vm_monitor_data`
- **API**:
  - `GET /status` — latest check result
  - `GET /history?hours=24` — historical data
  - `GET /health` — service health
- **Config** (env vars): `POLL_INTERVAL`, `TUNNEL_HOST`, `TUNNEL_PORT`, `VM_TAILSCALE_IP`

### Adding New Admin Widgets
1. Create service in `dashboard/<widget-name>/`
2. Add to `dashboard/docker-compose.yml`
3. Add nginx proxy route in `deploy/nginx/personal-website.conf`
4. Add health check in `deploy/run.sh`
5. Add widget card in the `admin_dashboard()` route in `website/app.py`

## Authentication

### My Zone (OAuth)
- GitHub OAuth app for dashboard access
- Credentials in `./github actions relevant creds` (legacy)
- Should migrate to pass manager

## Key Files

| File | Purpose |
|------|---------|
| `website/app.py` | Main FastHTML application (includes admin dashboard route) |
| `website/auth.py` | Auth logic: `check_auth()`, `is_admin()`, OAuth flow |
| `deploy/run.sh` | Deployment script |
| `deploy/nginx/personal-website.conf` | nginx configuration |
| `dashboard/docker-compose.yml` | Dashboard services (habit-tracker + vm-monitor) |
| `dashboard/vm-monitor/monitor.py` | VM uptime monitor service |
| `.github/workflows/deploy.yml` | CI/CD workflow |

## Debugging

### Main Site Issues
```bash
# Check Flask container
ssh root@72.60.218.33 "docker logs personal-website --tail 50"

# Check nginx
ssh root@72.60.218.33 "nginx -t && systemctl status nginx"
```

### Dashboard Issues
```bash
# Check dashboard containers
ssh root@72.60.218.33 "cd /var/www/personal-website/dashboard && docker-compose ps"
ssh root@72.60.218.33 "cd /var/www/personal-website/dashboard && docker-compose logs --tail 50"
```

### SSL Issues
If prabhanshu.space shows avantiterraform content (or vice versa):
```bash
# Check SSL status for both sites
ssh root@72.60.218.33 "certbot certificates"

# Force SSL reinstall for this site
# (Do this via deployment, not manually!)
```

## Cross-Machine Sync

This repo is cloned on both desktop and laptop. Before starting work:
```bash
git status
git fetch origin && git status
ssh laptop "cd ~/Programs/personal-website && git status --short"
```
