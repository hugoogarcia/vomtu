#!/bin/bash

# Vomtu VPS Auto-Setup Script
# Usage: curl -sSL https://raw.githubusercontent.com/hugoogarcia/vomtu/main/setup_vps.sh | bash

set -e

echo "🚀 Iniciando despliegue de VOMTU PRO MAX..."

# 1. Update system
sudo apt-get update
sudo apt-get install -y nginx git certbot python3-certbot-nginx

# 2. Prepare directory
sudo mkdir -p /var/www/vomtu
sudo chown -R $USER:$USER /var/www/vomtu

# 3. Clone or Update
if [ -d "/var/www/vomtu/.git" ]; then
    echo "🔄 Actualizando repositorio..."
    cd /var/www/vomtu
    git pull origin main
else
    echo "📥 Clonando repositorio..."
    git clone https://github.com/hugoogarcia/vomtu.git /var/www/vomtu
fi

# 4. Configure Nginx
echo "⚙️ Configurando Nginx para VOMTU..."
# We use a specific file for vomtu to avoid conflicts with other services like n8n
cat <<EOF | sudo tee /etc/nginx/sites-available/vomtu
server {
    listen 80;
    server_name vomtu.com www.vomtu.com;

    root /var/www/vomtu;
    index index.html;

    location / {
        try_files $uri $uri.html $uri/ =404;
    }

    # Optimization for videos
    location ~* \.(mp4|webm)$ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/vomtu /etc/nginx/sites-enabled/
# Removed: sudo rm -f /etc/nginx/sites-enabled/default (Dangerous for multi-site servers)

# 5. Restart Nginx
sudo nginx -t
sudo systemctl restart nginx

echo "✅ ¡Web desplegada con éxito en http://vomtu.com!"
echo "⚠️  RECUERDA: Tienes que apuntar el registro A de tu dominio en Hostinger a la IP: $(curl -s ifconfig.me)"
echo "🔐 Para poner el candadito (SSL), corre este comando cuando el dominio apunte aquí: sudo certbot --nginx -d vomtu.com -d www.vomtu.com"
