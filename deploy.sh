#/bin/bash

# Django backend + admin (gunicorn)
echo "Restarting Django backend..."
sudo systemctl restart kudo

# Telegram bot
echo "Restarting Telegram bot..."
sudo systemctl restart kudo_bot

echo "All services restarted!"
