# 🚀 Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Change SECRET_KEY in .env (use `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS with your domain
- [ ] Review and update CORS settings if needed
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie settings

### Database
- [ ] Migrate to PostgreSQL (recommended)
- [ ] Run all migrations on production database
- [ ] Create database backups
- [ ] Test database connection
- [ ] Set up automated backups

### Email
- [ ] Configure production email backend (SendGrid, Mailgun, AWS SES, etc.)
- [ ] Test email delivery
- [ ] Set up email monitoring
- [ ] Configure bounce handling
- [ ] Verify sender domain (SPF, DKIM, DMARC)

### Static Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure WhiteNoise or CDN for static files
- [ ] Test static file serving
- [ ] Optimize images

### Celery & Redis
- [ ] Set up Redis in production (or use managed service)
- [ ] Configure Celery workers as systemd services
- [ ] Set up Celery Beat for scheduled tasks
- [ ] Monitor task queue
- [ ] Configure task retry policies

## Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Create application user
sudo useradd -m -s /bin/bash crm_user
```

### 2. Application Deployment
```bash
# Clone/upload your code
cd /var/www/
sudo git clone <your-repo> crm-cryo
sudo chown -R crm_user:crm_user crm-cryo

# Set up virtual environment
cd crm-cryo
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE crm_cryo;
CREATE USER crm_user WITH PASSWORD 'your_secure_password';
ALTER ROLE crm_user SET client_encoding TO 'utf8';
ALTER ROLE crm_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE crm_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE crm_cryo TO crm_user;
\q

# Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

### 4. Gunicorn Setup
```bash
# Create systemd service file
sudo nano /etc/systemd/system/crm-cryo.service
```

```ini
[Unit]
Description=Cryo CRM Gunicorn daemon
After=network.target

[Service]
User=crm_user
Group=www-data
WorkingDirectory=/var/www/crm-cryo
Environment="PATH=/var/www/crm-cryo/venv/bin"
ExecStart=/var/www/crm-cryo/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/crm-cryo/crm_cryo.sock \
          crm_cryo.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable service
sudo systemctl start crm-cryo
sudo systemctl enable crm-cryo
```

### 5. Nginx Setup
```bash
sudo nano /etc/nginx/sites-available/crm-cryo
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/crm-cryo/staticfiles/;
    }

    location /media/ {
        alias /var/www/crm-cryo/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/crm-cryo/crm_cryo.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/crm-cryo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Setup (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 7. Celery Setup
```bash
# Celery Worker Service
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=crm_user
Group=www-data
WorkingDirectory=/var/www/crm-cryo
Environment="PATH=/var/www/crm-cryo/venv/bin"
ExecStart=/var/www/crm-cryo/venv/bin/celery -A crm_cryo worker -l info

[Install]
WantedBy=multi-user.target
```

```bash
# Celery Beat Service
sudo nano /etc/systemd/system/celerybeat.service
```

```ini
[Unit]
Description=Celery Beat
After=network.target

[Service]
Type=simple
User=crm_user
Group=www-data
WorkingDirectory=/var/www/crm-cryo
Environment="PATH=/var/www/crm-cryo/venv/bin"
ExecStart=/var/www/crm-cryo/venv/bin/celery -A crm_cryo beat -l info

[Install]
WantedBy=multi-user.target
```

```bash
# Start services
sudo systemctl start celery celerybeat
sudo systemctl enable celery celerybeat
```

## Post-Deployment

### Testing
- [ ] Test admin login
- [ ] Create test service
- [ ] Create test package
- [ ] Add test client
- [ ] Book test appointment
- [ ] Test email sending
- [ ] Verify scheduled tasks are running
- [ ] Check all admin sections

### Monitoring
- [ ] Set up error logging (Sentry)
- [ ] Configure server monitoring
- [ ] Set up uptime monitoring
- [ ] Monitor Celery queues
- [ ] Check Redis memory usage
- [ ] Monitor database performance

### Backups
- [ ] Set up automated database backups
- [ ] Test backup restoration
- [ ] Configure media file backups
- [ ] Document backup procedures

### Performance
- [ ] Enable gzip compression
- [ ] Configure browser caching
- [ ] Optimize database queries
- [ ] Add database indexes
- [ ] Monitor response times

## Environment Variables (Production)

```bash
# .env file for production
SECRET_KEY=<generate-new-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://crm_user:password@localhost:5432/crm_cryo

# Email (example with SendGrid)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<your-sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Maintenance

### Regular Tasks
- [ ] Weekly database backups verification
- [ ] Monthly security updates
- [ ] Quarterly dependency updates
- [ ] Monitor disk space
- [ ] Review error logs
- [ ] Clean up old sessions
- [ ] Archive old data

### Updating Application
```bash
# Pull latest code
cd /var/www/crm-cryo
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Restart services
sudo systemctl restart crm-cryo celery celerybeat
```

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status crm-cryo
sudo systemctl status celery
sudo systemctl status celerybeat
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u crm-cryo -f

# Celery logs
sudo journalctl -u celery -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Django Shell
```bash
cd /var/www/crm-cryo
source venv/bin/activate
python manage.py shell
```

## Security Hardening

- [ ] Configure firewall (ufw)
- [ ] Disable root SSH login
- [ ] Use SSH keys instead of passwords
- [ ] Keep system updated
- [ ] Regular security audits
- [ ] Monitor for suspicious activity
- [ ] Implement rate limiting
- [ ] Configure fail2ban

## Performance Optimization

- [ ] Enable database connection pooling
- [ ] Configure Redis maxmemory
- [ ] Set up database query caching
- [ ] Use CDN for static files
- [ ] Optimize Celery worker count
- [ ] Configure Gunicorn workers based on CPU cores

## Recommended Services

- **Hosting**: DigitalOcean, AWS, Linode, Heroku
- **Database**: Amazon RDS, DigitalOcean Managed Database
- **Email**: SendGrid, Mailgun, Amazon SES
- **Monitoring**: Sentry, New Relic, DataDog
- **Uptime**: UptimeRobot, Pingdom
- **CDN**: CloudFlare, Amazon CloudFront

---

**Ready for Production! 🎉**
