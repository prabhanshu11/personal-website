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

# Create/update .env for dashboard with GitHub token from secrets
echo "📝 Creating dashboard .env file..."
cat > .env << EOF
# Habit Tracker Backend
GITHUB_TOKEN=${HABITS_GITHUB_TOKEN:-ghp_placeholder_token}
REPO_ALLOWLIST=ALL
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=15

# Frontend (built into the image, not runtime)
# NEXT_PUBLIC_API_BASE=/dashboard/api
EOF

if [ "$HABITS_GITHUB_TOKEN" = "" ] || [ "$HABITS_GITHUB_TOKEN" = "ghp_placeholder_token" ]; then
    echo "⚠️  Warning: HABITS_GITHUB_TOKEN not provided. Dashboard may not fetch GitHub data."
else
    echo "✅ Dashboard .env configured with GitHub token from secrets"
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

# Always copy repo config and re-apply certbot SSL
# This ensures new routes (like /vm) are always picked up
# and certbot --reinstall re-adds SSL directives after config copy
sudo cp "$REPO_NGINX_CONF" "$NGINX_CONF"

if [ -f /etc/letsencrypt/live/prabhanshu.space/fullchain.pem ]; then
    sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --reinstall --redirect --non-interactive || true
else
    sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --non-interactive --agree-tos --redirect || true
fi

sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx config updated and reloaded"

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