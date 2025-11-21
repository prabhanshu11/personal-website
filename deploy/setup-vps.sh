#!/bin/bash

# One-time VPS setup script for prabhanshu.space
# Run this script ONCE on the VPS to set up everything

set -e  # Exit on error

echo "🔧 Starting VPS setup for prabhanshu.space..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required software..."
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    nginx \
    certbot \
    python3-certbot-nginx \
    build-essential \
    curl \
    git

# Install UV package manager
echo "📦 Installing UV package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Add UV to bashrc for future sessions
if ! grep -q ".local/bin" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

echo "✅ UV installed at: $(which uv)"

# Create application directory
echo "📁 Ensuring clean application directory..."
sudo rm -rf /var/www/prabhanshu.space/ # Remove existing directory
sudo mkdir -p /var/www/prabhanshu.space/ # Recreate it
sudo chown -R prabhanshu:www-data /var/www/prabhanshu.space
sudo chmod -R 755 /var/www/prabhanshu.space

# Clone repository
echo "📥 Cloning repository from GitHub..."
cd /var/www/prabhanshu.space
git clone https://github.com/prabhanshu11/personal-website.git .

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp deploy/nginx/personal-website.conf /etc/nginx/sites-available/prabhanshu.space

# Initialize UV and install dependencies
echo "📦 Installing Python dependencies..."
uv sync

# Enable site
sudo ln -sf /etc/nginx/sites-available/prabhanshu.space /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# Restart nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

# Configure systemd service
echo "⚙️  Configuring systemd service..."
sudo cp deploy/systemd/personal-website.service /etc/systemd/system/prabhanshu-website.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
echo "🚀 Starting application service..."
sudo systemctl enable prabhanshu-website
sudo systemctl start prabhanshu-website

# Check service status
echo "✅ Checking service status..."
sudo systemctl status prabhanshu-website --no-pager -l

# Wait a moment for app to start
sleep 3

# Setup SSL with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
echo "⚠️  Make sure DNS is pointing to this server before continuing!"
read -p "Press Enter to continue with SSL setup, or Ctrl+C to cancel..."

sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --non-interactive --agree-tos --email hello@prabhanshu.space --redirect

# Test SSL renewal
echo "🔍 Testing SSL certificate renewal..."
sudo certbot renew --dry-run

# Make deploy script executable
chmod +x /var/www/prabhanshu.space/deploy/run.sh

# Create deploy alias
if ! grep -q "alias deploy" ~/.bashrc; then
    echo "alias deploy='cd /var/www/prabhanshu.space && ./deploy/run.sh'" >> ~/.bashrc
fi

echo ""

echo "🎉 VPS setup completed successfully!"

echo ""

echo "📋 Summary:"
echo "  - Application directory: /var/www/prabhanshu.space"
echo "  - Nginx config: /etc/nginx/sites-available/prabhanshu.space"
echo "  - Systemd service: /etc/systemd/system/prabhanshu-website.service"
echo "  - Logs: sudo journalctl -u prabhanshu-website -f"
echo "  - Deploy command: deploy (or ./deploy/run.sh)"

echo ""

echo "🌐 Your website should now be live at:"
echo "  - https://prabhanshu.space"
echo "  - https://www.prabhanshu.space"

echo ""

echo "✅ Next steps:"
echo "  1. Visit your website to verify it's working"
echo "  2. Check SSL certificate: https://www.ssllabs.com/ssltest/analyze.html?d=prabhanshu.space"
echo "  3. To deploy updates: just run 'deploy' from anywhere"

