#!/bin/bash

# Script to fix n8n routing issue on Hostinger VPS
# This adds n8n.hugogarcia.cloud as a reverse proxy to port 5678

set -e

echo "🛠️ Configurando n8n en Nginx..."

# 1. Create n8n config file
cat <<EOF | sudo tee /etc/nginx/sites-available/n8n
server {
    listen 80;
    server_name n8n.hugogarcia.cloud;

    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket support (important for n8n)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# 2. Enable the site
sudo ln -sf /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/

# 3. Test and reload Nginx
echo "🔍 Verificando configuración..."
sudo nginx -t
sudo systemctl reload nginx

echo "✅ n8n configurado en http://n8n.hugogarcia.cloud"
echo "🔐 Para habilitar SSL (HTTPS), ejecuta:"
echo "sudo certbot --nginx -d n8n.hugogarcia.cloud"
