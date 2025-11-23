from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from services.models import ServiceType, Service
from packages.models import Package
from clients.models import Client
from appointments.models import Appointment
from discounts.models import Discount


class Command(BaseCommand):
    help = 'Load test data for services, packages, clients, and appointments'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading test data...')
        
        # Create Service Types
        self.stdout.write('Creating service types...')
        service_types_data = [
            {
                'name': 'Cryotherapy',
                'code': 'CRYO',
                'description': 'Whole body cryotherapy for recovery and wellness',
                'icon': 'fas fa-snowflake',
                'display_order': 1
            },
            {
                'name': 'Red Light Therapy',
                'code': 'RED_LIGHT',
                'description': 'Photobiomodulation therapy for skin and cellular health',
                'icon': 'fas fa-lightbulb',
                'display_order': 2
            },
            {
                'name': 'Infrared Sauna',
                'code': 'INFRARED',
                'description': 'Deep tissue heating for detoxification and relaxation',
                'icon': 'fas fa-fire',
                'display_order': 3
            },
            {
                'name': 'Oxygen Therapy',
                'code': 'OXYGEN',
                'description': 'Hyperbaric oxygen therapy for enhanced recovery',
                'icon': 'fas fa-wind',
                'display_order': 4
            },
        ]
        
        service_types = {}
        for st_data in service_types_data:
            st, created = ServiceType.objects.get_or_create(
                code=st_data['code'],
                defaults=st_data
            )
            service_types[st_data['code']] = st
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created service type: {st.name}'))
            else:
                self.stdout.write(f'  - Service type exists: {st.name}')
        
        # Create Services
        self.stdout.write('\nCreating services...')
        services_data = [
            {
                'name': 'Whole Body Cryotherapy - 3 Minutes',
                'service_type': service_types['CRYO'],
                'description': 'Full body exposure to extreme cold temperatures',
                'duration_minutes': 3,
                'base_price': Decimal('45.00'),
                'benefits': 'Reduces inflammation, boosts metabolism, improves recovery',
                'contraindications': 'Not suitable for pregnant women, people with heart conditions, or uncontrolled hypertension',
                'preparation_instructions': 'Wear dry undergarments, remove all jewelry'
            },
            {
                'name': 'Localized Cryotherapy - Spot Treatment',
                'service_type': service_types['CRYO'],
                'description': 'Targeted cold therapy for specific body areas',
                'duration_minutes': 10,
                'base_price': Decimal('25.00'),
                'benefits': 'Reduces pain and inflammation in specific areas',
                'contraindications': 'Avoid on open wounds or skin infections',
            },
            {
                'name': 'Red Light Therapy - Full Body',
                'service_type': service_types['RED_LIGHT'],
                'description': 'Full body red and near-infrared light exposure',
                'duration_minutes': 20,
                'base_price': Decimal('35.00'),
                'benefits': 'Improves skin health, reduces wrinkles, enhances cellular energy',
                'preparation_instructions': 'Remove makeup and expose skin directly to light'
            },
            {
                'name': 'Red Light Therapy - Facial',
                'service_type': service_types['RED_LIGHT'],
                'description': 'Concentrated red light therapy for face and neck',
                'duration_minutes': 15,
                'base_price': Decimal('30.00'),
                'benefits': 'Reduces fine lines, improves skin tone, stimulates collagen',
            },
            {
                'name': 'Infrared Sauna - 30 Minutes',
                'service_type': service_types['INFRARED'],
                'description': 'Relaxing infrared heat therapy session',
                'duration_minutes': 30,
                'base_price': Decimal('40.00'),
                'benefits': 'Detoxification, improved circulation, relaxation',
                'contraindications': 'Not for people with heat sensitivity or certain medications',
                'preparation_instructions': 'Hydrate well before session, bring towel'
            },
            {
                'name': 'Infrared Sauna - 45 Minutes',
                'service_type': service_types['INFRARED'],
                'description': 'Extended infrared heat therapy session',
                'duration_minutes': 45,
                'base_price': Decimal('55.00'),
                'benefits': 'Deep detoxification, muscle recovery, stress relief',
            },
            {
                'name': 'Oxygen Therapy - Standard Session',
                'service_type': service_types['OXYGEN'],
                'description': 'Breathe 95% pure oxygen with aromatherapy',
                'duration_minutes': 30,
                'base_price': Decimal('35.00'),
                'benefits': 'Increases energy, mental clarity, reduces stress',
                'preparation_instructions': 'No smoking 2 hours before session'
            },
            {
                'name': 'Oxygen Therapy - Extended Session',
                'service_type': service_types['OXYGEN'],
                'description': 'Extended oxygen therapy with relaxation',
                'duration_minutes': 60,
                'base_price': Decimal('60.00'),
                'benefits': 'Enhanced recovery, improved concentration, better sleep',
            },
        ]
        
        services = {}
        for svc_data in services_data:
            svc, created = Service.objects.get_or_create(
                name=svc_data['name'],
                defaults=svc_data
            )
            services[svc_data['name']] = svc
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created service: {svc.name}'))
            else:
                self.stdout.write(f'  - Service exists: {svc.name}')
        
        # Create Packages
        self.stdout.write('\nCreating packages...')
        packages_data = [
            {
                'name': 'Recovery Pro Package',
                'category': 'RECOVERY',
                'description': 'Ultimate recovery package combining cryotherapy and infrared sauna',
                'total_sessions': 10,
                'price': Decimal('750.00'),
                'validity_days': 90,
                'services': [
                    services['Whole Body Cryotherapy - 3 Minutes'],
                    services['Infrared Sauna - 30 Minutes'],
                ]
            },
            {
                'name': 'Fatigue Fighter',
                'category': 'ENERGY',
                'description': 'Boost energy and focus with cryo and oxygen therapy',
                'total_sessions': 10,
                'price': Decimal('650.00'),
                'validity_days': 60,
                'min_sessions_per_week': 2,
                'max_sessions_per_week': 3,
                'services': [
                    services['Whole Body Cryotherapy - 3 Minutes'],
                    services['Oxygen Therapy - Standard Session'],
                ]
            },
            {
                'name': 'Skin Rejuvenation Package',
                'category': 'BEAUTY',
                'description': 'Comprehensive skin health and anti-aging package',
                'total_sessions': 12,
                'price': Decimal('400.00'),
                'validity_days': 90,
                'services': [
                    services['Red Light Therapy - Full Body'],
                    services['Red Light Therapy - Facial'],
                ]
            },
            {
                'name': 'Wellness Starter',
                'category': 'GENERAL',
                'description': 'Introduction to wellness therapies',
                'total_sessions': 5,
                'price': Decimal('200.00'),
                'validity_days': 30,
                'services': [
                    services['Whole Body Cryotherapy - 3 Minutes'],
                    services['Red Light Therapy - Full Body'],
                    services['Infrared Sauna - 30 Minutes'],
                ]
            },
            {
                'name': 'Pain Relief Intensive',
                'category': 'PAIN',
                'description': 'Targeted pain management and inflammation reduction',
                'total_sessions': 8,
                'price': Decimal('280.00'),
                'validity_days': 45,
                'min_sessions_per_week': 2,
                'services': [
                    services['Whole Body Cryotherapy - 3 Minutes'],
                    services['Localized Cryotherapy - Spot Treatment'],
                ]
            },
        ]
        
        packages = {}
        for pkg_data in packages_data:
            pkg_services = pkg_data.pop('services')
            pkg, created = Package.objects.get_or_create(
                name=pkg_data['name'],
                defaults=pkg_data
            )
            if created:
                pkg.services.set(pkg_services)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created package: {pkg.name}'))
            else:
                self.stdout.write(f'  - Package exists: {pkg.name}')
            packages[pkg_data['name']] = pkg
        
        # Create Clients
        self.stdout.write('\nCreating test clients...')
        clients_data = [
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@example.com',
                'phone': '555-0101',
                'date_of_birth': timezone.now().date() - timedelta(days=365*32),
                'gender': 'F',
                'address_line1': '123 Wellness Ave',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94102',
                'medical_conditions': 'None reported',
                'notes': 'Interested in recovery and performance enhancement'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@example.com',
                'phone': '555-0102',
                'date_of_birth': timezone.now().date() - timedelta(days=365*28),
                'gender': 'M',
                'address_line1': '456 Health Street',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94103',
                'medical_conditions': 'Chronic back pain',
                'notes': 'Marathon runner, looking for recovery solutions'
            },
            {
                'first_name': 'Emma',
                'last_name': 'Williams',
                'email': 'emma.williams@example.com',
                'phone': '555-0103',
                'date_of_birth': timezone.now().date() - timedelta(days=365*45),
                'gender': 'F',
                'address_line1': '789 Beauty Blvd',
                'city': 'Oakland',
                'state': 'CA',
                'zip_code': '94601',
                'medications': 'Multivitamin',
                'notes': 'Focus on anti-aging and skin health'
            },
            {
                'first_name': 'James',
                'last_name': 'Rodriguez',
                'email': 'james.rodriguez@example.com',
                'phone': '555-0104',
                'date_of_birth': timezone.now().date() - timedelta(days=365*38),
                'gender': 'M',
                'address_line1': '321 Fitness Lane',
                'city': 'Berkeley',
                'state': 'CA',
                'zip_code': '94704',
                'medical_conditions': 'Mild hypertension (controlled)',
                'medications': 'Lisinopril 10mg',
                'notes': 'CrossFit athlete, very active'
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Anderson',
                'email': 'lisa.anderson@example.com',
                'phone': '555-0105',
                'date_of_birth': timezone.now().date() - timedelta(days=365*52),
                'gender': 'F',
                'address_line1': '654 Relax Road',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94105',
                'allergies': 'Pollen',
                'notes': 'Stress management and relaxation focus'
            },
        ]
        
        clients = {}
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            clients[client_data['email']] = client
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created client: {client.get_full_name()}'))
            else:
                self.stdout.write(f'  - Client exists: {client.get_full_name()}')
        
        # Create some sample appointments
        self.stdout.write('\nCreating sample appointments...')
        cryo_service = services['Whole Body Cryotherapy - 3 Minutes']
        sauna_service = services['Infrared Sauna - 30 Minutes']
        facial_service = services['Red Light Therapy - Facial']
        
        appointments_data = [
            {
                'client': clients['sarah.johnson@example.com'],
                'service': cryo_service,
                'appointment_date': timezone.now().date() + timedelta(days=1),
                'appointment_time': timezone.now().time().replace(hour=10, minute=0),
                'duration_minutes': cryo_service.duration_minutes,
                'status': 'SCHEDULED',
                'notes': 'First session'
            },
            {
                'client': clients['michael.chen@example.com'],
                'service': sauna_service,
                'appointment_date': timezone.now().date() + timedelta(days=2),
                'appointment_time': timezone.now().time().replace(hour=14, minute=0),
                'duration_minutes': sauna_service.duration_minutes,
                'status': 'SCHEDULED',
                'notes': 'Post-workout recovery'
            },
            {
                'client': clients['emma.williams@example.com'],
                'service': facial_service,
                'appointment_date': timezone.now().date() + timedelta(days=1),
                'appointment_time': timezone.now().time().replace(hour=11, minute=0),
                'duration_minutes': facial_service.duration_minutes,
                'status': 'SCHEDULED',
            },
        ]
        
        for appt_data in appointments_data:
            appt, created = Appointment.objects.get_or_create(
                client=appt_data['client'],
                service=appt_data['service'],
                appointment_date=appt_data['appointment_date'],
                appointment_time=appt_data['appointment_time'],
                defaults=appt_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created appointment for {appt.client.get_full_name()}'))
        
        # Create sample discounts
        self.stdout.write('\nCreating sample discounts...')
        discounts_data = [
            {
                'code': 'WELCOME20',
                'name': 'Welcome Discount',
                'discount_type': 'PERCENTAGE',
                'description': 'New client welcome discount - 20% off',
                'percentage_off': Decimal('20.00'),
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
                'is_active': True,
                'max_uses_total': 100,
            },
            {
                'code': 'REFER50',
                'name': 'Referral Reward',
                'discount_type': 'FIXED',
                'description': 'Referral program discount - $50 off',
                'fixed_amount_off': Decimal('50.00'),
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=180),
                'is_active': True,
            },
            {
                'code': 'BOGO',
                'name': 'Buy One Get One Free',
                'discount_type': 'BOGO',
                'description': 'Buy one session, get one free',
                'free_sessions': 1,
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=60),
                'is_active': True,
                'max_uses_per_client': 1,
            },
        ]
        
        for disc_data in discounts_data:
            disc, created = Discount.objects.get_or_create(
                code=disc_data['code'],
                defaults=disc_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created discount: {disc.name}'))
            else:
                self.stdout.write(f'  - Discount exists: {disc.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test data loaded successfully!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  - Service Types: {ServiceType.objects.count()}')
        self.stdout.write(f'  - Services: {Service.objects.count()}')
        self.stdout.write(f'  - Packages: {Package.objects.count()}')
        self.stdout.write(f'  - Clients: {Client.objects.count()}')
        self.stdout.write(f'  - Appointments: {Appointment.objects.count()}')
        self.stdout.write(f'  - Discounts: {Discount.objects.count()}')
