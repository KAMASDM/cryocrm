from django.core.management.base import BaseCommand
from services.models import Service
from packages.models import Package
from discounts.models import Discount
from communications.models import EmailTemplate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Loads initial data for the CRM system'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')
        
        # Create Services
        self.stdout.write('Creating services...')
        services = [
            {
                'name': 'Whole Body Cryotherapy',
                'service_type': 'CRYO',
                'description': 'Experience the benefits of extreme cold therapy for recovery and wellness.',
                'duration_minutes': 3,
                'base_price': Decimal('65.00'),
                'benefits': 'Reduces inflammation, accelerates recovery, boosts metabolism, improves mood',
                'contraindications': 'Pregnancy, severe hypertension, heart conditions, cold allergies',
            },
            {
                'name': 'Red Light Therapy',
                'service_type': 'RED_LIGHT',
                'description': 'Therapeutic wavelengths of light to promote healing and rejuvenation.',
                'duration_minutes': 20,
                'base_price': Decimal('45.00'),
                'benefits': 'Improves skin health, reduces wrinkles, enhances collagen production, reduces pain',
                'contraindications': 'Photosensitivity, certain medications',
            },
            {
                'name': 'Infrared Sauna Session',
                'service_type': 'INFRARED',
                'description': 'Detoxify and relax with gentle infrared heat therapy.',
                'duration_minutes': 30,
                'base_price': Decimal('55.00'),
                'benefits': 'Detoxification, weight loss, pain relief, improved circulation, stress reduction',
                'contraindications': 'Pregnancy, cardiovascular conditions, alcohol consumption',
            },
            {
                'name': 'Oxygen Therapy',
                'service_type': 'OXYGEN',
                'description': 'Breathe pure oxygen to enhance physical and mental performance.',
                'duration_minutes': 15,
                'base_price': Decimal('40.00'),
                'benefits': 'Increases energy, improves focus, accelerates recovery, enhances athletic performance',
                'contraindications': 'COPD, emphysema without medical supervision',
            },
        ]
        
        service_objects = {}
        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            service_objects[service.service_type] = service
            if created:
                self.stdout.write(f'  ✓ Created: {service.name}')
            else:
                self.stdout.write(f'  - Already exists: {service.name}')
        
        # Create Packages
        self.stdout.write('\nCreating packages...')
        packages_data = [
            {
                'name': 'Fatigue / Focus / Energy Package',
                'category': 'ENERGY',
                'description': 'Boost your energy levels and mental clarity with cryotherapy and oxygen therapy.',
                'services': ['CRYO', 'OXYGEN'],
                'total_sessions': 10,
                'min_sessions_per_week': 2,
                'max_sessions_per_week': 3,
                'price': Decimal('850.00'),
                'validity_days': 60,
                'can_combine_services': False,
            },
            {
                'name': 'Pain and Inflammation Package',
                'category': 'PAIN',
                'description': 'Combat pain and reduce inflammation with targeted cryotherapy and red light therapy.',
                'services': ['CRYO', 'RED_LIGHT'],
                'total_sessions': 12,
                'min_sessions_per_week': 3,
                'max_sessions_per_week': 4,
                'price': Decimal('1100.00'),
                'validity_days': 45,
                'can_combine_services': True,
            },
            {
                'name': 'Injury Recovery and Prevention',
                'category': 'INJURY',
                'description': 'Accelerate recovery and prevent future injuries with our specialized protocol.',
                'services': ['CRYO', 'OXYGEN'],
                'total_sessions': 10,
                'min_sessions_per_week': 2,
                'max_sessions_per_week': 3,
                'price': Decimal('880.00'),
                'validity_days': 60,
                'can_combine_services': False,
            },
            {
                'name': 'Beauty and Skin Health',
                'category': 'BEAUTY',
                'description': 'Rejuvenate your skin and enhance your natural beauty from within.',
                'services': ['RED_LIGHT', 'CRYO', 'OXYGEN', 'INFRARED'],
                'total_sessions': 10,
                'min_sessions_per_week': 2,
                'max_sessions_per_week': 3,
                'price': Decimal('950.00'),
                'validity_days': 60,
                'can_combine_services': False,
            },
            {
                'name': 'Wellbeing and Stress Relief',
                'category': 'WELLNESS',
                'description': 'Find your balance and reduce stress with our comprehensive wellness package.',
                'services': ['CRYO', 'OXYGEN', 'INFRARED'],
                'total_sessions': 10,
                'min_sessions_per_week': 2,
                'max_sessions_per_week': 3,
                'price': Decimal('920.00'),
                'validity_days': 60,
                'can_combine_services': False,
            },
        ]
        
        for package_data in packages_data:
            service_types = package_data.pop('services')
            package, created = Package.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            
            if created:
                # Add services to package
                for service_type in service_types:
                    if service_type in service_objects:
                        package.services.add(service_objects[service_type])
                
                self.stdout.write(f'  ✓ Created: {package.name}')
            else:
                self.stdout.write(f'  - Already exists: {package.name}')
        
        # Create Email Templates
        self.stdout.write('\nCreating email templates...')
        templates = [
            {
                'name': 'Appointment Reminder',
                'template_type': 'REMINDER',
                'subject': 'Reminder: Your appointment at Wellness Center',
                'html_content': open('/Users/jigardesai/Desktop/crm-cryo/templates/emails/appointment_reminder.html').read(),
                'available_variables': 'client_name, appointment_date, appointment_time, service_name, duration',
            },
            {
                'name': 'Package Expiry Warning',
                'template_type': 'PACKAGE_EXPIRY',
                'subject': 'Your wellness package is expiring soon!',
                'html_content': open('/Users/jigardesai/Desktop/crm-cryo/templates/emails/package_expiry.html').read(),
                'available_variables': 'client_name, package_name, expiry_date, sessions_remaining',
            },
            {
                'name': 'Birthday Greeting',
                'template_type': 'BIRTHDAY',
                'subject': '🎉 Happy Birthday from Wellness Center!',
                'html_content': open('/Users/jigardesai/Desktop/crm-cryo/templates/emails/birthday.html').read(),
                'available_variables': 'client_name, age',
            },
        ]
        
        for template_data in templates:
            try:
                template, created = EmailTemplate.objects.get_or_create(
                    name=template_data['name'],
                    defaults=template_data
                )
                if created:
                    self.stdout.write(f'  ✓ Created: {template.name}')
                else:
                    self.stdout.write(f'  - Already exists: {template.name}')
            except FileNotFoundError:
                self.stdout.write(f'  ✗ Template file not found for: {template_data["name"]}')
        
        # Create Sample Discounts
        self.stdout.write('\nCreating sample discounts...')
        discounts = [
            {
                'name': 'Refer a Friend - 20% Off',
                'code': 'REFER20',
                'description': 'Get 20% off when you refer a friend',
                'discount_type': 'PERCENTAGE',
                'applies_to': 'ALL',
                'percentage_off': Decimal('20.00'),
                'max_uses_per_client': 5,
            },
            {
                'name': 'First Time Client - $50 Off',
                'code': 'FIRST50',
                'description': 'First-time clients get $50 off any package',
                'discount_type': 'FIXED',
                'applies_to': 'PACKAGE',
                'fixed_amount_off': Decimal('50.00'),
                'max_uses_per_client': 1,
            },
            {
                'name': 'Buy 10 Get 1 Free',
                'code': 'BONUS1',
                'description': 'Purchase any package and get 1 free session',
                'discount_type': 'FREE_SESSION',
                'applies_to': 'PACKAGE',
                'free_sessions': 1,
                'max_uses_per_client': 1,
            },
        ]
        
        for discount_data in discounts:
            discount, created = Discount.objects.get_or_create(
                code=discount_data['code'],
                defaults=discount_data
            )
            if created:
                self.stdout.write(f'  ✓ Created: {discount.name}')
            else:
                self.stdout.write(f'  - Already exists: {discount.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initial data loaded successfully!'))
