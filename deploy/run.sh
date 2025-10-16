#!/bin/bash

# Deploy script for prabhanshu.space
# Run this on the VPS after pushing changes

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /var/www/prabhanshu.space

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Update dependencies with uv
echo "📦 Updating dependencies..."
uv sync

# Restart the service
echo "🔄 Restarting application..."
sudo systemctl restart prabhanshu-website

# Wait a moment for service to start
sleep 2

# Check status
echo "✅ Checking application status..."
sudo systemctl status prabhanshu-website --no-pager -l

# Check if app is responding
echo "🔍 Testing application response..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "❌ Application health check failed!"
    exit 1
fi

echo "🎉 Deployment completed successfully!"