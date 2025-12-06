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
│   └── app.py              # Main FastHTML application
├── deploy/
│   ├── nginx/              # Nginx configuration
│   ├── systemd/            # Systemd service
│   ├── setup-vps.sh        # One-time VPS setup script
│   └── run.sh              # Deployment script
├── tests/                  # Test files (future)
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