#!/bin/bash

# Deploy script for prabhanshu.space
# Run this on the VPS after pushing changes

set -e  # Exit on error

echo "🚀 Starting Docker deployment..."

# Navigate to project directory
cd /var/www/prabhanshu.space

# Note: git pull is handled by the CI workflow (deploy.yml) BEFORE
# running this script, to avoid the self-modifying script problem
# where bash reads the old script from memory after git pull updates it.

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

# Copy repo config (includes SSL directives and HTTPS redirect)
# No certbot needed during deploy — certs are managed by certbot timer
sudo cp "$REPO_NGINX_CONF" "$NGINX_CONF"

# If nginx -t fails, temporarily disable broken sibling site configs
# (remove symlink from sites-enabled, re-create after reload)
DISABLED_SITES=""
if ! sudo nginx -t 2>/dev/null; then
    echo "⚠️  nginx -t failed. Isolating broken site configs..."
    for conf in /etc/nginx/sites-enabled/*; do
        site="$(basename "$conf")"
        [ "$site" = "prabhanshu.space" ] && continue
        target="$(readlink -f "$conf")"
        sudo rm "$conf"
        if sudo nginx -t 2>/dev/null; then
            echo "  Isolated broken config: $site"
            DISABLED_SITES="$DISABLED_SITES $conf=$target"
        else
            # Not this one, restore symlink
            sudo ln -s "$target" "$conf"
        fi
    done
fi

if sudo nginx -t 2>&1; then
    sudo systemctl reload nginx
    echo "✅ Nginx config updated and reloaded"
else
    echo "❌ nginx -t still failing:"
    sudo nginx -t 2>&1 || true
fi

# Restore disabled symlinks (sites stay broken until their own deploy fixes them)
for entry in $DISABLED_SITES; do
    conf="${entry%%=*}"
    target="${entry##*=}"
    sudo ln -s "$target" "$conf" 2>/dev/null || true
    echo "  Restored symlink: $(basename "$conf") (still broken, needs its own fix)"
done

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