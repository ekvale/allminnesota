# Deploy All Minnesota to 147.182.227.124

## 1. On the server (Ubuntu/Debian)

**Goal:** Run the app as a dedicated non-root user (`allminnesota`), not as root.

### Create app user (do this first — don’t run the app as root)

Create a dedicated user that will own the app and run Gunicorn:

```bash
# -m = create home dir, -s = shell (so you can su to this user for deploys)
sudo useradd -m -s /bin/bash allminnesota
# Optional: set a password if you want to SSH as this user later
# sudo passwd allminnesota
```

### Install system packages (as root/sudo)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql libpq-dev
```

### Create app directory and give it to the app user

```bash
sudo mkdir -p /var/www/allminnesota
sudo chown allminnesota:allminnesota /var/www/allminnesota
```

### PostgreSQL database (as root/sudo — do before migrating as allminnesota)

```bash
sudo -u postgres psql
```

In psql:

```sql
CREATE USER allminnesota WITH PASSWORD 'your_secure_password';
CREATE DATABASE allminnesota_db OWNER allminnesota;
\q
```

Use the same user/password/db name in `DATABASE_URL` in `.env` when you create it below.

### Clone repo and set up Python (as `allminnesota`)

Switch to the app user and do all app setup so nothing runs as root:

```bash
sudo su - allminnesota
cd /var/www/allminnesota
git clone https://github.com/ekvale/allminnesota.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create .env (production)

```bash
cp .env.example .env
nano .env
```

Set at least:

- `SECRET_KEY` — long random string (e.g. `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `DEBUG=False`
- `ALLOWED_HOSTS=147.182.227.124`
- `DATABASE_URL=postgres://allminnesota:your_secure_password@localhost:5432/allminnesota_db` (match the PostgreSQL user/password you created above)

### Migrate and static files (still as `allminnesota`)

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
# Exit back to your normal user when done
exit
```

### Let Nginx read static/media (run as root/sudo)

Nginx runs as `www-data` and needs to serve static and media files owned by `allminnesota`:

```bash
sudo chmod -R o+rX /var/www/allminnesota/staticfiles /var/www/allminnesota/media 2>/dev/null || true
```

### Install and enable Gunicorn systemd service (as root/sudo)

Gunicorn runs as **allminnesota** (not root). It binds to `127.0.0.1:8000`; nginx proxies to it.

```bash
sudo cp /var/www/allminnesota/deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-allminnesota
sudo systemctl start gunicorn-allminnesota
```

### Nginx (as root/sudo)

```bash
sudo cp /var/www/allminnesota/deploy/nginx-allminnesota.conf /etc/nginx/sites-available/allminnesota
sudo ln -s /etc/nginx/sites-available/allminnesota /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 2. Future deploys (after code changes)

Deploy as the app user so you’re not using root:

```bash
sudo su - allminnesota
cd /var/www/allminnesota
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit
sudo chmod -R o+rX /var/www/allminnesota/staticfiles /var/www/allminnesota/media 2>/dev/null || true
sudo systemctl restart gunicorn-allminnesota
```

If you SSH in as a different user (e.g. `ubuntu`) and that user has sudo, you can do the app steps with `sudo -u allminnesota`:

```bash
cd /var/www/allminnesota
sudo -u allminnesota git pull
sudo -u allminnesota bash -c 'cd /var/www/allminnesota && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput'
sudo chmod -R o+rX /var/www/allminnesota/staticfiles /var/www/allminnesota/media 2>/dev/null || true
sudo systemctl restart gunicorn-allminnesota
```

## 3. Optional: deploy script

Run this script as a user that can use `sudo` for the restart (e.g. from your SSH user, not root). It runs the app steps as `allminnesota`:

```bash
#!/bin/bash
set -e
cd /var/www/allminnesota
sudo -u allminnesota git pull
sudo -u allminnesota bash -c 'cd /var/www/allminnesota && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput'
sudo chmod -R o+rX /var/www/allminnesota/staticfiles /var/www/allminnesota/media 2>/dev/null || true
sudo systemctl restart gunicorn-allminnesota
echo "Deploy done."
```

Save as `deploy/deploy.sh`, then `chmod +x deploy/deploy.sh` and run `./deploy/deploy.sh` for each deploy (from a user with sudo).
