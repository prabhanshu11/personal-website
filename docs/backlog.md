# Backlog

## High Priority

- [ ] Fix orphan `calendar.prabhanshu.space` nginx config on VPS
  - Config at `/etc/nginx/sites-available/calendar.prabhanshu.space` declares `listen 443 ssl` with no certificate
  - Blocks `nginx -t` globally — currently isolated by personal-website deploy script
  - **Calendar architecture**: Pi runs calendar app on :8080, autossh tunnels Pi:8080 → VPS:8081, VPS nginx proxies `life.prabhanshu.space` → localhost:8081
  - `calendar.prabhanshu.space` is NOT the same as `life.prabhanshu.space` — it's an orphan with no managing repo
  - Options: remove the orphan config, or provision a cert and point it somewhere
  - LAN access: connect to Pi directly; internet access: Pi → VPS tunnel

## Normal

- [ ] Add tests for deployment pipeline
