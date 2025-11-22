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

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t personal-website .

# Stop and remove existing container
echo "🛑 Stopping existing container..."
docker stop personal-website || true
docker rm personal-website || true

# Run new container
echo "▶️  Running new container..."
docker run -d \
  --name personal-website \
  --restart always \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  personal-website

# Wait a moment for service to start
sleep 5

# Check if app is responding
echo "🔍 Testing application response..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "❌ Application health check failed!"
    # Print logs for debugging
    docker logs personal-website
    exit 1
fi

echo "🎉 Docker deployment completed successfully!"