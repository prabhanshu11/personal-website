#!/bin/bash

# One-time VPS setup script for prabhanshu.space
# Run this script ONCE on the VPS to set up everything
# PRE-REQUISITES:
# 1. SSH into VPS as root (or user with sudo)
# 2. Copy the entire 'deploy' directory to the VPS:
#    scp -r deploy root@<vps-ip>:~/
#    (Ensure 'github actions relevant creds' is inside deploy/)

set -e  # Exit on error

echo "🔧 Starting VPS setup for prabhanshu.space..."

# --- Configuration ---
APP_DIR="/var/www/prabhanshu.space"
DEPLOY_USER="deploy"
REPO_URL="https://github.com/prabhanshu11/personal-website.git"

# --- 1. User Setup ---
echo "👤 Configuring users..."

# Create deploy user if not exists
if id "$DEPLOY_USER" &>/dev/null; then
    echo "   User '$DEPLOY_USER' already exists."
else
    echo "   Creating user '$DEPLOY_USER'..."
    sudo useradd -m -s /bin/bash "$DEPLOY_USER"
    # Set a password for deploy user (optional, better to use keys)
    # echo "$DEPLOY_USER:deploy_password" | sudo chpasswd
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required software..."
sudo apt install -y \
    python3 python3-venv python3-pip \
    nginx certbot python3-certbot-nginx \
    build-essential curl git ca-certificates gnupg \
    acl  # For setfacl if needed

# --- 2. Docker Setup ---
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Configure Docker permissions
echo "🐳 Configuring Docker permissions..."
sudo usermod -aG docker "$DEPLOY_USER"
sudo usermod -aG docker "$USER" 2>/dev/null || true

# --- 3. UV Setup ---
echo "📦 Installing UV package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
# Make sure deploy user has uv available (optional, mostly relevant for local dev logic)
# docker usually handles the build environment.

# --- 4. Directory & Permissions ---
echo "📁 Configuring application directory..."
sudo mkdir -p "$APP_DIR"
# Set ownership to deploy user
sudo chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR"
# Ensure correct permissions
sudo chmod -R 755 "$APP_DIR"
# Allow www-data (Nginx) to read (if it were serving static files directly, but we proxy)

# --- 5. Code Setup ---
echo "📥 Cloning/Updating repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "   Repo exists, pulling latest..."
    sudo -u "$DEPLOY_USER" git -C "$APP_DIR" pull origin main
else
    echo "   Cloning fresh..."
    # We clear the directory first to avoid conflicts, EXCEPT .env if it exists
    if [ -f "$APP_DIR/.env" ]; then
        sudo mv "$APP_DIR/.env" /tmp/prabhanshu_env_backup
    fi
    sudo rm -rf "${APP_DIR:?}/"* "${APP_DIR:?}/".* 2>/dev/null || true
    
    sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR"
    
    if [ -f /tmp/prabhanshu_env_backup ]; then
        sudo mv /tmp/prabhanshu_env_backup "$APP_DIR/.env"
        sudo chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR/.env"
    fi
fi

# --- 6. Environment Variables (Automated) ---
echo "🔐 Configuring environment variables..."
CRED_FILE="./github actions relevant creds" # Expecting it in current dir
ENV_FILE="$APP_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "   .env file not found at $ENV_FILE"
    if [ -f "$CRED_FILE" ]; then
        echo "   Found credentials file! Generating .env..."
        
        # EXTRACT CREDENTIALS (Basic parsing based on known format)
        # Format: Prabhanshu My Zone (ID, SECRET) ...
        # We'll just take the first pair for Prod
        LINE=$(cat "$CRED_FILE" | grep "Prabhanshu My Zone")
        CLIENT_ID=$(echo "$LINE" | grep -oP '(?<=Prabhanshu My Zone \()[^,]+')
        CLIENT_SECRET=$(echo "$LINE" | grep -oP '(?<=, )[^)]+' | head -1) # Simple extraction
        
        # Fallback if grep failed (manual check recommended in that case)
        if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
             echo "   ⚠️  Could not auto-parse credentials. Please create .env manually."
        else
            SECRET_KEY=$(openssl rand -hex 32)
            
            # Create .env content
            cat <<EOF | sudo -u "$DEPLOY_USER" tee "$ENV_FILE" > /dev/null
GITHUB_CLIENT_ID=$CLIENT_ID
GITHUB_CLIENT_SECRET=$CLIENT_SECRET
SECRET_KEY=$SECRET_KEY
EOF
            echo "   ✅ .env created successfully with Prod keys."
        fi
    else
        echo "   ⚠️  Credentials file '$CRED_FILE' not found in current directory."
        echo "   PLEASE CREATE $ENV_FILE MANUALLY with GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, SECRET_KEY."
    fi
else
    echo "   ✅ .env file already exists."
fi

# --- 7. Nginx & Systemd ---
echo "🌐 Configuring Nginx..."
sudo cp "$APP_DIR/deploy/nginx/personal-website.conf" /etc/nginx/sites-available/prabhanshu.space
sudo ln -sf /etc/nginx/sites-available/prabhanshu.space /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "⚙️  Configuring systemd service..."
# Important: Service should run as 'deploy' user ideally, or root if docker requires it (docker group handles it)
sudo cp "$APP_DIR/deploy/systemd/personal-website.service" /etc/systemd/system/prabhanshu-website.service
sudo systemctl daemon-reload
sudo systemctl enable prabhanshu-website
sudo systemctl restart prabhanshu-website

# --- 8. SSL ---
echo "🔒 Setting up SSL..."
if [ ! -f /etc/letsencrypt/live/prabhanshu.space/fullchain.pem ]; then
    echo "   Requesting new certificate..."
    sudo certbot --nginx -d prabhanshu.space -d www.prabhanshu.space --non-interactive --agree-tos --email hello@prabhanshu.space --redirect
else
    echo "   Certificate already exists."
fi

# --- 9. Utilities ---
echo "🔗 Creating shortcuts..."
chmod +x "$APP_DIR/deploy/run.sh"
sudo ln -sf "$APP_DIR/deploy/run.sh" /usr/local/bin/deploy

echo "🎉 VPS setup completed successfully!"
echo "------------------------------------------------"
echo "Next steps:"
echo "1. Verify the site is running: https://prabhanshu.space"
echo "2. If you used the 'deploy' user for the first time, set up SSH keys for it:"
echo "   mkdir -p /home/deploy/.ssh && chmod 700 /home/deploy/.ssh"
echo "   cp ~/.ssh/authorized_keys /home/deploy/.ssh/ && chown -R deploy:deploy /home/deploy/.ssh"
echo "------------------------------------------------"

