#!/bin/bash
set -e
cd /root/kudo/kudo_backend
echo "Pulling..."
git pull origin main
echo "Dependencies..."
pip install -r requirements.txt --break-system-packages -q
echo "Static files..."
python3 manage.py collectstatic --noinput -v 0
echo "Migrations..."
python3 manage.py migrate --noinput
echo "Restarting..."
sudo systemctl restart kudo
sudo systemctl restart kudo_bot
echo "✓ Deploy tugadi! https://kudo.uz"
