# Server Bootstrap (Ubuntu, Linode/Akamai)

One-time setup to prepare a fresh Linode for CI/CD deploys and HTTPS.

Assumptions
- Domain: prabhanshu.space (and www.prabhanshu.space)
- Email for TLS: mail.prabhanshu@gmail.com
- App path: /srv/apps/personal-website
- Service user: deploy

0) Create Linode (Cloud Manager UI)
- Choose Ubuntu LTS (22.04 or 24.04), region close to you, Nanode 1GB is fine.
- Add your SSH key to root.
- Boot and note the public IPv4 (and IPv6 if enabled).

1) DNS at Namecheap (UI)
- Remove the URL Redirect record for `@` and the CNAME `www -> parkingpage.namecheap.com`.
- Add A record: Host `@` → <YOUR_SERVER_IPV4>, TTL 30 min.
- Add CNAME: Host `www` → `@` (or A to the same IPv4), TTL 30 min.
- Wait a few minutes; verify: `dig +short prabhanshu.space` should show your IPv4.

2) Create non-root deploy user (SSH to server as root)
```bash
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
nano /home/deploy/.ssh/authorized_keys  # paste your PUBLIC deploy key
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
```

Optional (recommended): allow passwordless sudo for service mgmt
```bash
echo 'deploy ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/sbin/nginx, /usr/sbin/certbot' > /etc/sudoers.d/deploy
chmod 440 /etc/sudoers.d/deploy
```

3) Base packages, firewall, uv, nginx, certbot
```bash
apt-get update
apt-get install -y nginx ufw curl git python3-pip

ufw allow OpenSSH
ufw allow 'Nginx Full'
yes | ufw enable

curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile.d/uv.sh
```

4) App directories and ownership
```bash
mkdir -p /srv/apps/personal-website/{app,deploy,logs}
chown -R deploy:deploy /srv/apps/personal-website
```

5) Nginx site and TLS
```bash
# Place nginx conf
cp /srv/apps/personal-website/app/deploy/nginx/personal-website.conf /etc/nginx/sites-available/personal-website
ln -s /etc/nginx/sites-available/personal-website /etc/nginx/sites-enabled/personal-website || true
nginx -t && systemctl reload nginx

apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d prabhanshu.space -d www.prabhanshu.space \
  -m mail.prabhanshu@gmail.com --agree-tos --no-eff-email
```

6) Systemd service
```bash
cp /srv/apps/personal-website/app/deploy/systemd/personal-website.service /etc/systemd/system/personal-website.service
chmod +x /srv/apps/personal-website/deploy/run.sh
systemctl daemon-reload
systemctl enable --now personal-website
```

7) First manual sync (optional, before CI)
- As `deploy` user, you can clone or copy the repo into `/srv/apps/personal-website/app` to test the service.

8) CI secrets (GitHub repo → Settings → Secrets and variables → Actions)
- SERVER_HOST: <YOUR_SERVER_IPV4>
- SERVER_USER: deploy
- SSH_PRIVATE_KEY: the private key that matches the authorized_keys above
- SSH_KNOWN_HOSTS: output of `ssh-keyscan -t ed25519 <YOUR_SERVER_IPV4>`

Then push to main to trigger CI/CD.

