from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_appointment_reminder(appointment_id):
    """Send appointment reminder email"""
    from appointments.models import Appointment
    from .models import EmailTemplate, ScheduledEmail
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if reminder already sent
        if appointment.reminder_sent:
            return f"Reminder already sent for appointment {appointment_id}"
        
        # Get reminder template
        template = EmailTemplate.objects.filter(
            template_type='REMINDER',
            is_active=True
        ).first()
        
        if not template:
            return "No active reminder template found"
        
        # Prepare context
        context = {
            'client_name': appointment.client.get_full_name(),
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'service_name': appointment.service.name,
            'duration': appointment.duration_minutes,
        }
        
        # Render template
        rendered = template.render(context)
        
        # Create and send scheduled email
        scheduled_email = ScheduledEmail.objects.create(
            client=appointment.client,
            email_type='REMINDER',
            template=template,
            scheduled_for=timezone.now(),
            subject=rendered['subject'],
            rendered_html=rendered['html'],
            rendered_text=rendered['text'],
            appointment=appointment
        )
        
        if scheduled_email.send():
            appointment.reminder_sent = True
            appointment.reminder_sent_at = timezone.now()
            appointment.save()
            return f"Reminder sent for appointment {appointment_id}"
        else:
            return f"Failed to send reminder for appointment {appointment_id}"
            
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"


@shared_task
def send_daily_reminders():
    """Send reminders for appointments in the next 24 hours"""
    from appointments.models import Appointment
    from datetime import datetime
    
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status__in=['SCHEDULED', 'CONFIRMED'],
        reminder_sent=False,
        client__email_notifications=True
    )
    
    count = 0
    for appointment in appointments:
        send_appointment_reminder.delay(appointment.id)
        count += 1
    
    return f"Queued {count} appointment reminders"


@shared_task
def send_package_expiry_warnings():
    """Send warnings for packages expiring soon"""
    from packages.models import PackagePurchase
    from .models import EmailTemplate, ScheduledEmail
    
    # Get packages expiring in 7 days
    warning_date = timezone.now().date() + timedelta(days=7)
    
    expiring_packages = PackagePurchase.objects.filter(
        expiry_date=warning_date,
        status='ACTIVE',
        client__email_notifications=True
    )
    
    template = EmailTemplate.objects.filter(
        template_type='PACKAGE_EXPIRY',
        is_active=True
    ).first()
    
    if not template:
        return "No active package expiry template found"
    
    count = 0
    for package_purchase in expiring_packages:
        context = {
            'client_name': package_purchase.client.get_full_name(),
            'package_name': package_purchase.package.name,
            'expiry_date': package_purchase.expiry_date,
            'sessions_remaining': package_purchase.sessions_remaining,
        }
        
        rendered = template.render(context)
        
        ScheduledEmail.objects.create(
            client=package_purchase.client,
            email_type='PACKAGE_EXPIRY',
            template=template,
            scheduled_for=timezone.now(),
            subject=rendered['subject'],
            rendered_html=rendered['html'],
            rendered_text=rendered['text'],
            package_purchase=package_purchase
        )
        count += 1
    
    return f"Created {count} package expiry warnings"


@shared_task
def send_birthday_greetings():
    """Send birthday greetings to clients"""
    from clients.models import Client
    from .models import EmailTemplate, ScheduledEmail
    
    today = timezone.now().date()
    
    birthday_clients = Client.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        is_active=True,
        marketing_emails=True
    )
    
    template = EmailTemplate.objects.filter(
        template_type='BIRTHDAY',
        is_active=True
    ).first()
    
    if not template:
        return "No active birthday template found"
    
    count = 0
    for client in birthday_clients:
        context = {
            'client_name': client.get_full_name(),
            'age': client.get_age(),
        }
        
        rendered = template.render(context)
        
        ScheduledEmail.objects.create(
            client=client,
            email_type='BIRTHDAY',
            template=template,
            scheduled_for=timezone.now(),
            subject=rendered['subject'],
            rendered_html=rendered['html'],
            rendered_text=rendered['text']
        )
        count += 1
    
    return f"Created {count} birthday greetings"


@shared_task
def send_email_campaign(campaign_id):
    """Send an email campaign"""
    from .models import EmailCampaign, EmailLog
    
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        
        if campaign.status not in ['DRAFT', 'SCHEDULED']:
            return f"Campaign {campaign_id} cannot be sent (status: {campaign.status})"
        
        campaign.status = 'SENDING'
        campaign.save()
        
        recipients = campaign.get_recipients()
        campaign.total_recipients = recipients.count()
        campaign.save()
        
        for client in recipients:
            context = {
                'client_name': client.get_full_name(),
                'client_email': client.email,
            }
            
            rendered = campaign.template.render(context)
            
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.conf import settings
                
                email = EmailMultiAlternatives(
                    subject=rendered['subject'],
                    body=rendered['text'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[client.email]
                )
                
                if rendered['html']:
                    email.attach_alternative(rendered['html'], "text/html")
                
                email.send()
                
                campaign.emails_sent += 1
                
                # Log the email
                EmailLog.objects.create(
                    client=client,
                    subject=rendered['subject'],
                    sent_to=client.email,
                    email_type='CAMPAIGN',
                    campaign=campaign,
                    sent_successfully=True
                )
                
            except Exception as e:
                campaign.emails_failed += 1
                
                # Log the failure
                EmailLog.objects.create(
                    client=client,
                    subject=rendered['subject'],
                    sent_to=client.email,
                    email_type='CAMPAIGN',
                    campaign=campaign,
                    sent_successfully=False,
                    error_message=str(e)
                )
        
        campaign.status = 'SENT'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return f"Campaign {campaign_id} sent to {campaign.emails_sent} recipients"
        
    except EmailCampaign.DoesNotExist:
        return f"Campaign {campaign_id} not found"


@shared_task
def process_scheduled_emails():
    """Process and send scheduled emails"""
    from .models import ScheduledEmail
    
    pending_emails = ScheduledEmail.objects.filter(
        status='PENDING',
        scheduled_for__lte=timezone.now()
    )
    
    sent_count = 0
    failed_count = 0
    
    for email in pending_emails:
        if email.send():
            sent_count += 1
        else:
            failed_count += 1
    
    return f"Processed scheduled emails: {sent_count} sent, {failed_count} failed"
