#!/bin/bash
# Deploy script: run as a user with sudo (e.g. your SSH user). App steps run as 'allminnesota'.
set -e
cd /var/www/allminnesota
sudo -u allminnesota git pull
sudo -u allminnesota bash -c 'cd /var/www/allminnesota && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput'
sudo chmod -R o+rX /var/www/allminnesota/staticfiles /var/www/allminnesota/media 2>/dev/null || true
sudo systemctl restart gunicorn-allminnesota
echo "Deploy done."
