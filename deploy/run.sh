#!/bin/bash

# Deploy script for prabhanshu.space
# Run this on the VPS after pushing changes

set -e  # Exit on error

echo "🚀 Starting Docker deployment..."

# Navigate to project directory
cd /var/www/prabhanshu.space

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# ==========================================
# MAIN WEBSITE
# ==========================================
echo "🐳 Building main website Docker image..."
docker build -t personal-website .

echo "🛑 Stopping existing main website container..."
docker stop personal-website || true
docker rm personal-website || true

echo "▶️  Running main website container..."
docker run -d \
  --name personal-website \
  --restart always \
  -p 8000:8000 \
  -v newsletter_data:/app/data \
  --env-file .env \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  personal-website

# ==========================================
# DASHBOARD (Habit Tracker)
# ==========================================
echo "🐳 Building and deploying dashboard containers..."
cd dashboard

# Create .env for dashboard if it doesn't exist (copy from example)
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating dashboard .env from example..."
        cp .env.example .env
        echo "⚠️  Warning: Dashboard .env created from example. Update GITHUB_TOKEN for full functionality."
    fi
fi

# Build and start dashboard containers
docker compose down || true
docker compose build
docker compose up -d

cd ..

# ==========================================
# NGINX CONFIG UPDATE
# ==========================================
echo "🔧 Updating nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/prabhanshu.space"
REPO_NGINX_CONF="deploy/nginx/personal-website.conf"

# Always backup existing config with timestamp
sudo cp "$NGINX_CONF" "${NGINX_CONF}.bak.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

# Check if nginx config has outdated dashboard routes (with trailing slash)
if grep -q "location /dashboard/habits/" "$NGINX_CONF" 2>/dev/null; then
    echo "📝 Detected old nginx config (trailing slash) - updating..."
    # Copy new config
    sudo cp "$REPO_NGINX_CONF" "$NGINX_CONF"
    # Re-run certbot to add SSL if needed (non-interactive)
    sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --non-interactive --agree-tos --redirect || true
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx config updated and reloaded"
elif ! grep -q "dashboard/habits" "$NGINX_CONF" 2>/dev/null; then
    echo "📝 Dashboard routes not found - adding..."
    sudo cp "$REPO_NGINX_CONF" "$NGINX_CONF"
    sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --non-interactive --agree-tos --redirect || true
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx config updated with dashboard routes"
else
    echo "✅ Nginx config is already up to date"
fi

# ==========================================
# HEALTH CHECKS
# ==========================================
echo "🔍 Waiting for services to start..."
sleep 5

echo "🔍 Testing main website..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Main website is healthy!"
else
    echo "❌ Main website health check failed!"
    docker logs personal-website
    exit 1
fi

echo "🔍 Testing dashboard backend..."
if curl -f http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ Dashboard backend is healthy!"
else
    echo "⚠️  Dashboard backend not responding (may need GITHUB_TOKEN in .env)"
    docker logs dashboard-habit-backend 2>/dev/null || true
fi

echo "🔍 Testing dashboard frontend..."
if curl -f http://localhost:5173/dashboard/habits > /dev/null 2>&1; then
    echo "✅ Dashboard frontend is healthy!"
else
    echo "⚠️  Dashboard frontend not responding"
    docker logs dashboard-habit-frontend 2>/dev/null || true
fi

echo "🎉 Docker deployment completed successfully!"