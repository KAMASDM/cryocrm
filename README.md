# Cryo Therapy CRM System

A comprehensive Customer Relationship Management (CRM) system built with Django for wellness businesses offering cryotherapy, red light therapy, infrared sauna, and oxygen therapy services.

## Features

### 🎯 Core Functionality

#### Service Management
- Create and manage individual services (Cryotherapy, Red Light Therapy, Infrared Sauna, Oxygen Therapy)
- Configure service pricing, duration, and descriptions
- Track service benefits, contraindications, and preparation instructions

#### Package Management
- Create custom treatment packages combining multiple services
- Pre-configured package categories:
  - **Fatigue/Focus/Energy**: Cryotherapy + Oxygen Therapy (10 sessions)
  - **Pain and Inflammation**: Cryotherapy + Red Light Therapy (12 sessions)
  - **Injury Recovery**: Cryotherapy + Oxygen Therapy (10 sessions)
  - **Beauty and Skin Health**: Multiple services (10 sessions)
  - **Wellbeing and Stress Relief**: Multiple services (10 sessions)
- Set session frequency requirements (min/max per week)
- Configure package validity periods
- Track package purchases and usage

#### Client Management
- Comprehensive client profiles with medical history
- Track appointments, package purchases, and session history
- Client communication preferences
- Referral tracking with unique referral codes
- Lifetime value calculation
- Emergency contact information

#### Appointment Scheduling
- Book appointments for individual services or package sessions
- Multiple appointment statuses (Scheduled, Confirmed, Checked In, In Progress, Completed, Cancelled, No Show)
- Automatic session tracking for package purchases
- Client feedback and rating system
- Appointment history tracking

#### Discount System
- Flexible discount types:
  - Percentage discounts
  - Fixed amount discounts
  - Free sessions
  - Buy One Get One (BOGO)
- Apply discounts to specific packages, services, or all purchases
- Usage limits (total and per client)
- Stackable discounts option
- Referral program with automatic reward tracking

#### Email & Communication System
- Email templates for various purposes:
  - Appointment reminders
  - Appointment confirmations
  - Follow-up emails
  - Marketing campaigns
  - Newsletters
  - Birthday greetings
  - Package expiry warnings
  - Welcome emails
- Automated scheduled emails
- Email campaign management with targeting options
- Email tracking (sent, opened, clicked)
- Comprehensive email logs

#### Data Visualization & Reports
- Revenue analytics
- Appointment statistics
- Client acquisition metrics
- Package performance reports
- Email campaign analytics

## Installation

### Prerequisites

- Python 3.10 or higher
- Redis (for Celery task queue)
- PostgreSQL (recommended for production) or SQLite (for development)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd /Users/jigardesai/Desktop/crm-cryo
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # Email Configuration
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # Database (optional, uses SQLite by default)
   DATABASE_URL=postgresql://user:password@localhost/crm_cryo
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data (optional)**
   ```bash
   python manage.py loaddata initial_services.json
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery worker (in a separate terminal)**
   ```bash
   celery -A crm_cryo worker -l info
   ```

10. **Start Celery Beat (in a separate terminal)**
    ```bash
    celery -A crm_cryo beat -l info
    ```

11. **Start Redis** (if not already running)
    ```bash
    redis-server
    ```

## Usage

### Accessing the Admin Panel

1. Navigate to `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. The Jazzmin-powered admin interface will provide access to all CRM features

### Setting Up Services

1. Go to **Services** in the admin panel
2. Click "Add Service"
3. Fill in service details:
   - Name (e.g., "Whole Body Cryotherapy")
   - Service Type (CRYO, RED_LIGHT, INFRARED, OXYGEN)
   - Duration and pricing
   - Benefits and instructions

### Creating Packages

1. Go to **Packages**
2. Click "Add Package"
3. Select package category and add services
4. Configure session requirements and pricing
5. Set validity period

### Managing Clients

1. Go to **Clients**
2. Add new clients with contact information
3. Track medical information and preferences
4. View client history and lifetime value

### Scheduling Appointments

1. Go to **Appointments**
2. Select client and service
3. Choose date and time
4. Optionally link to a package purchase
5. Track appointment status through completion

### Setting Up Discounts

1. Go to **Discounts**
2. Create discount codes with specific rules
3. Set validity periods and usage limits
4. Apply to specific packages or services

### Email Campaigns

1. Create email templates in **Email Templates**
2. Set up campaigns in **Email Campaigns**
3. Select target audience
4. Schedule or send immediately

### Automated Tasks

The system automatically handles:
- Daily appointment reminders (9 AM)
- Package expiry warnings (10 AM)
- Birthday greetings (8 AM)
- Processing scheduled emails (every 15 minutes)

## Project Structure

```
crm-cryo/
├── crm_cryo/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── services/              # Service management
│   ├── models.py
│   └── admin.py
├── packages/              # Package management
│   ├── models.py
│   └── admin.py
├── clients/               # Client management
│   ├── models.py
│   └── admin.py
├── appointments/          # Appointment scheduling
│   ├── models.py
│   ├── admin.py
│   └── signals.py
├── discounts/             # Discount system
│   ├── models.py
│   └── admin.py
├── communications/        # Email system
│   ├── models.py
│   ├── admin.py
│   └── tasks.py
├── manage.py
└── requirements.txt
```

## Customization

### Jazzmin Theme

The admin interface is powered by Jazzmin. Customize the look and feel in `settings.py` under `JAZZMIN_SETTINGS` and `JAZZMIN_UI_TWEAKS`.

### Email Templates

Email templates support Django template syntax with variables like:
- `{{ client_name }}`
- `{{ appointment_date }}`
- `{{ service_name }}`
- `{{ package_name }}`

### Adding New Service Types

Edit `services/models.py` and add to `SERVICE_TYPES`:
```python
SERVICE_TYPES = [
    # ... existing types
    ('NEW_TYPE', 'New Service Type'),
]
```

## Production Deployment

### Environment Variables

Set these environment variables in production:
- `SECRET_KEY`: Generate a secure random key
- `DEBUG=False`
- `ALLOWED_HOSTS`: Your domain names
- Database credentials
- Email service credentials
- Redis URL

### Static Files

```bash
python manage.py collectstatic
```

### Database

Use PostgreSQL in production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_cryo',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Web Server

Use Gunicorn with Nginx:
```bash
gunicorn crm_cryo.wsgi:application --bind 0.0.0.0:8000
```

## Backup and Maintenance

### Database Backup

```bash
python manage.py dumpdata > backup.json
```

### Restore Database

```bash
python manage.py loaddata backup.json
```

## Support and Documentation

### Key Models

- **Service**: Individual wellness services
- **Package**: Treatment packages with multiple services
- **Client**: Customer profiles and information
- **Appointment**: Scheduled sessions
- **PackagePurchase**: Client package purchases and session tracking
- **Discount**: Promotional discounts and offers
- **EmailTemplate**: Reusable email templates
- **EmailCampaign**: Marketing email campaigns

### Admin Actions

- Bulk appointment status updates
- Send reminders to multiple appointments
- Mark referrals as completed/rewarded
- Cancel scheduled emails

## License

Proprietary - All rights reserved

## Version

1.0.0 - Initial Release

---

Built with ❤️ using Django 4.2 and Jazzmin
