# Quick Start Guide - Cryo Therapy CRM

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd /Users/jigardesai/Desktop/crm-cryo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### Step 4: Load Sample Data (Optional)
```bash
python manage.py load_initial_data
```
This will create:
- 4 services (Cryotherapy, Red Light, Infrared Sauna, Oxygen)
- 5 pre-configured packages
- 3 sample discounts
- 3 email templates

### Step 5: Run the Server
```bash
python manage.py runserver
```
Access the admin panel at: http://localhost:8000/admin/

### Step 6: Setup Background Tasks (Optional)

**Terminal 2 - Start Redis:**
```bash
redis-server
```

**Terminal 3 - Start Celery Worker:**
```bash
celery -A crm_cryo worker -l info
```

**Terminal 4 - Start Celery Beat (Scheduled Tasks):**
```bash
celery -A crm_cryo beat -l info
```

## 📋 First Tasks in the Admin

### 1. Add Your First Service
- Go to **Services** → **Add Service**
- Fill in: Name, Type, Price, Duration
- Save

### 2. Create a Package
- Go to **Packages** → **Add Package**
- Select services, set pricing and session requirements
- Save

### 3. Add a Client
- Go to **Clients** → **Add Client**
- Fill in contact information
- Save

### 4. Schedule an Appointment
- Go to **Appointments** → **Add Appointment**
- Select client, service, date, and time
- Save

### 5. Set Up Email Templates
- Go to **Email Templates** → View the pre-loaded templates
- Customize as needed

## 🎨 Customizing the Admin

The admin interface uses **Jazzmin**. To customize:

Edit `crm_cryo/settings.py` and modify `JAZZMIN_SETTINGS`:
- Change site title and branding
- Modify color scheme
- Adjust navigation menu
- Add custom links

## 📧 Email Configuration

Edit `.env` file:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an "App Password"
3. Use the app password in the configuration

## 🔄 Automated Tasks

Once Celery Beat is running, these tasks run automatically:
- **Daily 9:00 AM**: Send appointment reminders
- **Daily 10:00 AM**: Send package expiry warnings
- **Daily 8:00 AM**: Send birthday greetings
- **Every 15 minutes**: Process scheduled emails

## 📊 Key Features to Explore

### Package Management
- Create packages with multiple services
- Set session frequencies (min/max per week)
- Track package usage automatically
- Set validity periods

### Discount System
- Percentage or fixed amount discounts
- Free session offers
- Referral tracking
- Usage limits per client

### Client Management
- Comprehensive profiles
- Medical history tracking
- Lifetime value calculation
- Referral codes

### Email Marketing
- Reusable templates
- Campaign management
- Targeted sending
- Email tracking

## 🐛 Troubleshooting

### Database Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --no-input
```

### Celery Not Working
Make sure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Port Already in Use
```bash
python manage.py runserver 8080
```

## 📱 Common Workflows

### Booking from a Package
1. Client purchases package (Packages → Package Purchases)
2. Book appointment and link to the package purchase
3. System automatically decrements sessions

### Setting Up Referral Program
1. Create referral discount (Discounts)
2. When client refers someone, create Referral record
3. Mark as completed when referred client books
4. Apply discount to referrer

### Running Email Campaign
1. Create email template (Email Templates)
2. Create campaign (Email Campaigns)
3. Select target audience
4. Schedule or send immediately

## 🎯 Next Steps

1. ✅ Complete the setup above
2. 📝 Customize email templates with your branding
3. 🎨 Adjust Jazzmin theme colors
4. 👥 Add your first clients
5. 📅 Start booking appointments
6. 📧 Test email functionality
7. 📊 Monitor analytics in the dashboard

## 💡 Pro Tips

- Use the search bar in admin to quickly find clients
- Bulk actions let you update multiple appointments at once
- Email logs help track delivery issues
- Use filters to segment clients for targeted campaigns
- Export data using the admin's built-in export feature

## 🆘 Need Help?

Check the main README.md for detailed documentation of all features.

---

**Happy CRM'ing! 🎉**
