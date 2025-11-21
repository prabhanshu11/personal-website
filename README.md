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

### Initial VPS Setup (One-time)

```bash
# SSH into VPS
ssh prabhanshu @72.60.218.33

# Run setup script
bash setup-vps.sh
```

This will:
- Install all required software (Python, nginx, certbot, UV)
- Clone the repository
- Configure nginx reverse proxy
- Set up systemd service
- Obtain SSL certificate from Let's Encrypt
- Start the application

### Deploy Updates

**From local machine:**

```bash
# Make changes to code
git add .
git commit -m "Your commit message"
git push origin main
```

**On VPS:**

```bash
# SSH into VPS
ssh prabhanshu @72.60.218.33

# Run deploy script
deploy

# Or manually:
cd /var/www/prabhanshu.space
./deploy/deploy.sh
```

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