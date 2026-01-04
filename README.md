# Personal Website - prabhanshu.space

A modern personal website built with Python and FastHTML, deployed on a VPS with nginx, SSL, and systemd.

## 🌐 Live Site

**Visit:** [https://prabhanshu.space](https://prabhanshu.space)

## 🛠️ Tech Stack

- **Framework:** FastHTML (Python)
- **Server:** Uvicorn (ASGI)
- **Reverse Proxy:** Nginx
- **SSL:** Let's Encrypt (Certbot)
- **Package Manager:** UV
- **Process Manager:** Systemd
- **Hosting:** Hostinger VPS (Debian 13)
- **DNS:** Namecheap

## 📁 Project Structure

```
personal-website/
├── website/
│   ├── __init__.py
│   ├── app.py              # Main FastHTML application
│   ├── auth.py             # GitHub OAuth authentication
│   └── db.py               # SQLite database layer
├── dashboard/              # Life Dashboard (Docker container)
│   ├── docker-compose.yml  # Orchestrates habit-tracker services
│   ├── Dockerfile.backend  # FastAPI backend
│   ├── Dockerfile.frontend # Next.js frontend
│   ├── .env.example        # Environment template
│   └── habit-tracker/      # Habit tracker source (backend + web)
├── deploy/
│   ├── nginx/              # Nginx configuration
│   ├── systemd/            # Systemd service
│   ├── setup-vps.sh        # One-time VPS setup script
│   └── run.sh              # Deployment script
├── data/                   # SQLite database
├── tests/                  # Test files
├── pyproject.toml          # UV/Python project config
├── .gitignore
└── README.md
```

## 🚀 Local Development

### Prerequisites

- Python 3.12+
- UV package manager

### Setup

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/prabhanshu11/personal-website.git
cd personal-website

# Install dependencies
uv sync

# Run development server
uv run python -m src.app

# Or with debug mode
DEBUG=True uv run python -m src.app
```

Visit: http://localhost:8000

### Running with Life Dashboard

The Life Dashboard embeds the habit tracker (GitHub activity) in the private zone.

```bash
# Terminal 1: Personal website
DEBUG=True uv run python -m website.app

# Terminal 2: Habit tracker backend
cd dashboard/habit-tracker/backend
uv sync
PYTHONPATH=src uv run uvicorn habits_api.app:app --port 8081

# Terminal 3: Habit tracker frontend
cd dashboard/habit-tracker/web
npm install && npm run dev
```

With DEBUG=True, the iframe points directly to localhost:5173. In production, Nginx proxies `/dashboard/habits/` and `/dashboard/api/`.

## 🌐 Deployment

### Initial VPS Setup (Fresh Install)

1.  **Prepare Local Files**:
    Ensure you have `github actions relevant creds` inside the `deploy/` directory.

2.  **Copy Files to VPS**:
    Run this from your local machine:
    ```bash
    # Copy the deploy directory to the VPS (as root/sudo user)
    scp -r deploy root@<vps-ip>:~/
    ```

3.  **Run Setup Script**:
    SSH into the VPS and run the script:
    ```bash
    ssh root@<vps-ip>
    cd deploy
    ./setup-vps.sh
    ```
    
    *This script will:*
    - Create a `deploy` user.
    - Install Docker, Nginx, UV, etc.
    - Set up permissions.
    - **Auto-create `.env`** using the credentials file you uploaded.
    - Deploy the application.

### Deploy Updates

**Option 1: Automatic (GitHub Actions)**
Just push to the `main` branch.

**Option 2: Manual (SCP)**
If you prefer not to use GitHub Actions:
```bash
# Push code to VPS
ssh deploy@<vps-ip> "cd /var/www/prabhanshu.space && git pull"
# Or if git isn't set up, scp files...

# Run deploy
ssh deploy@<vps-ip> "deploy"
```

### Deploy Updates

**Option 1: Automatic (Recommended)**
Just push to the `main` branch! GitHub Actions will automatically:
1.  SSH into the VPS.
2.  Pull the latest code.
3.  Rebuild the Docker container.
4.  Restart the application.

**Option 2: Manual**
If you need to trigger a deploy manually:

```bash
# SSH into VPS
ssh prabhanshu@72.60.218.33

# Run deploy command
deploy
```

This runs the `deploy/run.sh` script which handles the Docker build and restart process.

## ⚙️ GitHub Actions Deployment

### Overview

The repository uses GitHub Actions to automatically deploy on push to `main`. The workflow:
1. Sets up SSH agent with the deploy key
2. Adds VPS to known hosts
3. SSHes into VPS and runs `./deploy/run.sh`

### Workflow File

Location: `.github/workflows/deploy.yml`

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Add VPS to known hosts
        run: |
          mkdir -p ~/.ssh
          ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy via SSH
        run: |
          ssh ${{ secrets.VPS_USERNAME }}@${{ secrets.VPS_HOST }} "cd /var/www/prabhanshu.space && ./deploy/run.sh"
```

### Required Secrets

Set these in: `Settings > Secrets and variables > Actions > Repository secrets`

| Secret | Description | Example |
|--------|-------------|---------|
| `VPS_HOST` | VPS IP address | `72.60.218.33` |
| `VPS_USERNAME` | SSH username | `root` |
| `SSH_PRIVATE_KEY` | Private SSH key (**PEM format**) | See below |

### ⚠️ CRITICAL: SSH Key Format

**The SSH key MUST be in PEM format, not OPENSSH format.**

| Format | Header | Works? |
|--------|--------|--------|
| **PEM** (classic) | `-----BEGIN RSA PRIVATE KEY-----` | ✅ Yes |
| **OPENSSH** (new) | `-----BEGIN OPENSSH PRIVATE KEY-----` | ❌ No |

Many SSH actions (including `appleboy/ssh-action` and some versions of `webfactory/ssh-agent`) fail to parse the newer OPENSSH format, resulting in cryptic errors like `ssh: no key found`.

### Generating a Compatible Key

```bash
# Generate RSA key in PEM format (compatible with GitHub Actions)
ssh-keygen -t rsa -b 4096 -m PEM -f ~/.ssh/deploy_key -N "" -C "github-actions-deploy"

# View private key (add this to GitHub secret)
cat ~/.ssh/deploy_key

# View public key (add this to VPS authorized_keys)
cat ~/.ssh/deploy_key.pub

# Add public key to VPS
cat ~/.ssh/deploy_key.pub | ssh root@<VPS_IP> "cat >> ~/.ssh/authorized_keys"

# Test the key works
ssh -i ~/.ssh/deploy_key root@<VPS_IP> "echo SUCCESS"
```

### Setting Secrets via CLI (Recommended)

Using `gh` CLI avoids copy-paste formatting issues:

```bash
# Authenticate gh CLI
gh auth login

# Set secrets
gh secret set VPS_HOST --repo <username>/<repo> --body "<VPS_IP>"
gh secret set VPS_USERNAME --repo <username>/<repo> --body "root"
gh secret set SSH_PRIVATE_KEY --repo <username>/<repo> --body "$(cat ~/.ssh/deploy_key)"
```

### Debugging Failed Workflows

```bash
# List recent workflow runs
gh run list --limit 5

# View logs for a specific run
gh run view <RUN_ID> --log-failed

# Manually trigger workflow
gh workflow run deploy.yml --ref main
```

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ssh: no key found` | Key in OPENSSH format | Generate key with `-m PEM` flag |
| `ssh: handshake failed: unable to authenticate` | Public key not on VPS | Add public key to `~/.ssh/authorized_keys` on VPS |
| `ssh-keyscan` fails | VPS_HOST secret is wrong | Update VPS_HOST via `gh secret set` |
| `Permission denied` | Key mismatch | Verify key fingerprints match on both sides |

### Verifying Key Fingerprints

```bash
# Local key fingerprint
ssh-keygen -lf ~/.ssh/deploy_key

# VPS authorized_keys fingerprints
ssh root@<VPS_IP> "ssh-keygen -lf ~/.ssh/authorized_keys"

# Both should show the same SHA256 hash for the deploy key
```

### Why Not `appleboy/ssh-action`?

We initially used `appleboy/ssh-action` but switched to `webfactory/ssh-agent` because:
1. `appleboy/ssh-action` had issues parsing OPENSSH format keys
2. `webfactory/ssh-agent` is more reliable and widely used
3. Separating SSH setup from command execution gives clearer error messages

## 🔧 Useful Commands

### On VPS

```bash
# Check application status
sudo systemctl status prabhanshu-website

# View application logs
sudo journalctl -u prabhanshu-website -f

# Restart application
sudo systemctl restart prabhanshu-website

# Check nginx status
sudo systemctl status nginx

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Check SSL certificate
sudo certbot certificates

# Renew SSL certificate (manual)
sudo certbot renew
```

## 🔍 Monitoring

- **Application Health:** https://prabhanshu.space/health
- **Nginx Access Logs:** `/var/log/nginx/prabhanshu.space.access.log`
- **Nginx Error Logs:** `/var/log/nginx/prabhanshu.space.error.log`
- **Application Logs:** `sudo journalctl -u prabhanshu-website -f`

## 🔒 SSL/HTTPS

SSL certificate is automatically managed by Let's Encrypt and renews every 60 days.

**Test SSL:**
- Browser: Visit https://prabhanshu.space (check padlock icon)
- SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=prabhanshu.space

## 🐛 Troubleshooting

### Application not starting

```bash
# Check logs
sudo journalctl -u prabhanshu-website -n 50

# Check if port 8000 is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart prabhanshu-website
```

### 502 Bad Gateway

```bash
# Check if application is running
sudo systemctl status prabhanshu-website

# Check nginx logs
sudo tail -f /var/log/nginx/prabhanshu.space.error.log
```

### DNS not resolving

```bash
# Check DNS from local machine
dig prabhanshu.space
dig www.prabhanshu.space

# Should return: 72.60.218.33
```

## 📝 License

MIT License - feel free to use this as a template for your own website!

## 👤 Author

**Prabhanshu**
- Website: [prabhanshu.space](https://prabhanshu.space)
- GitHub: [ @prabhanshu11](https://github.com/prabhanshu11)
- Email: hello @prabhanshu.space
