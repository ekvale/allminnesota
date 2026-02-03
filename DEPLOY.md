# Deploy All Minnesota to 147.182.227.124

## 1. On the server (Ubuntu/Debian)

### Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql libpq-dev
```

### Create app user and directory

```bash
sudo useradd -r -s /bin/false www-data  # often already exists
sudo mkdir -p /var/www/allminnesota
sudo chown $USER:$USER /var/www/allminnesota
cd /var/www/allminnesota
```

### Clone repo and set up Python

```bash
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
- `DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/allminnesota_db`

### PostgreSQL database

```bash
sudo -u postgres psql
```

In psql:

```sql
CREATE USER allminnesota WITH PASSWORD 'your_secure_password';
CREATE DATABASE allminnesota_db OWNER allminnesota;
\q
```

Use the same user/password/db name in `DATABASE_URL` in `.env`.

### Migrate and static files

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Install and enable Gunicorn systemd service

Gunicorn binds to `127.0.0.1:8000`; nginx proxies to it.

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/
# Edit paths if your app is not in /var/www/allminnesota:
# sudo nano /etc/systemd/system/gunicorn-allminnesota.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-allminnesota
sudo systemctl start gunicorn-allminnesota
```

### Nginx

```bash
sudo cp deploy/nginx-allminnesota.conf /etc/nginx/sites-available/allminnesota
sudo ln -s /etc/nginx/sites-available/allminnesota /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Permissions (if using www-data to run Gunicorn)

```bash
sudo chown -R www-data:www-data /var/www/allminnesota
# In gunicorn.service, User=www-data and WorkingDirectory/ExecStart paths correct
sudo systemctl restart gunicorn-allminnesota
```

## 2. Future deploys (after code changes)

```bash
cd /var/www/allminnesota
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-allminnesota
```

## 3. Optional: deploy script

Save as `deploy/deploy.sh` on the server and run from `/var/www/allminnesota`:

```bash
#!/bin/bash
set -e
cd /var/www/allminnesota
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-allminnesota
echo "Deploy done."
```

Then: `chmod +x deploy/deploy.sh` and run `./deploy/deploy.sh` for each deploy.
