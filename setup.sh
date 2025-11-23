#!/bin/bash

# Cryo Therapy CRM - Setup Script
# This script automates the initial setup process

echo "🏥 Cryo Therapy CRM - Initial Setup"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✓ Python detected: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your settings"
fi

# Run migrations
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo ""
echo "👤 Creating superuser account..."
echo "Please enter your admin credentials:"
python manage.py createsuperuser

# Load initial data
echo ""
read -p "📊 Load sample data (services, packages, discounts)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py load_initial_data
fi

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then visit: http://localhost:8000/admin/"
echo ""
echo "📧 For email functionality, configure .env with your email settings"
echo ""
echo "🔄 For background tasks (reminders, campaigns), in separate terminals run:"
echo "   redis-server"
echo "   celery -A crm_cryo worker -l info"
echo "   celery -A crm_cryo beat -l info"
echo ""
echo "📖 See QUICKSTART.md for more information"
echo ""
