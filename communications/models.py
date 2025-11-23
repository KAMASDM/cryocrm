from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class EmailTemplate(models.Model):
    """Email templates for different communications"""
    
    TEMPLATE_TYPES = [
        ('REMINDER', 'Appointment Reminder'),
        ('CONFIRMATION', 'Appointment Confirmation'),
        ('FOLLOWUP', 'Follow-up Email'),
        ('MARKETING', 'Marketing Email'),
        ('NEWSLETTER', 'Newsletter'),
        ('BIRTHDAY', 'Birthday Greeting'),
        ('WELCOME', 'Welcome Email'),
        ('PACKAGE_EXPIRY', 'Package Expiry Warning'),
        ('REFERRAL', 'Referral Program'),
        ('CUSTOM', 'Custom Email'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    
    # Email content
    html_content = models.TextField(
        help_text="HTML email content. Use {{variable}} for dynamic content."
    )
    text_content = models.TextField(
        blank=True,
        help_text="Plain text version of the email"
    )
    
    # Template variables
    available_variables = models.TextField(
        blank=True,
        help_text="Comma-separated list of available variables (e.g., client_name, appointment_date)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type', 'name']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render(self, context):
        """Render the template with given context"""
        from django.template import Template, Context
        
        html_template = Template(self.html_content)
        html_rendered = html_template.render(Context(context))
        
        text_rendered = ""
        if self.text_content:
            text_template = Template(self.text_content)
            text_rendered = text_template.render(Context(context))
        
        return {
            'subject': self.subject,
            'html': html_rendered,
            'text': text_rendered
        }


class EmailCampaign(models.Model):
    """Marketing email campaigns"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('SENDING', 'Sending'),
        ('SENT', 'Sent'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.PROTECT,
        related_name='campaigns'
    )
    
    # Targeting
    send_to_all = models.BooleanField(
        default=False,
        help_text="Send to all active clients"
    )
    target_clients = models.ManyToManyField(
        'clients.Client',
        blank=True,
        related_name='email_campaigns',
        help_text="Specific clients to send to"
    )
    
    # Filters
    only_marketing_subscribers = models.BooleanField(
        default=True,
        help_text="Only send to clients who opted in for marketing emails"
    )
    only_active_clients = models.BooleanField(
        default=True,
        help_text="Only send to active clients"
    )
    
    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to send the campaign"
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.PositiveIntegerField(default=0)
    emails_sent = models.PositiveIntegerField(default=0)
    emails_failed = models.PositiveIntegerField(default=0)
    emails_opened = models.PositiveIntegerField(default=0)
    links_clicked = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    def get_recipients(self):
        """Get list of recipients based on targeting criteria"""
        from clients.models import Client
        
        if self.send_to_all:
            recipients = Client.objects.all()
        else:
            recipients = self.target_clients.all()
        
        if self.only_active_clients:
            recipients = recipients.filter(is_active=True)
        
        if self.only_marketing_subscribers:
            recipients = recipients.filter(marketing_emails=True)
        
        return recipients


class ScheduledEmail(models.Model):
    """Individual scheduled emails (reminders, follow-ups, etc.)"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    EMAIL_TYPES = [
        ('REMINDER', 'Appointment Reminder'),
        ('FOLLOWUP', 'Follow-up'),
        ('BIRTHDAY', 'Birthday'),
        ('PACKAGE_EXPIRY', 'Package Expiry'),
        ('CUSTOM', 'Custom'),
    ]
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='scheduled_emails'
    )
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.PROTECT,
        related_name='scheduled_emails'
    )
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Content
    subject = models.CharField(max_length=200)
    rendered_html = models.TextField(blank=True)
    rendered_text = models.TextField(blank=True)
    
    # Related objects
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scheduled_emails'
    )
    package_purchase = models.ForeignKey(
        'packages.PackagePurchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scheduled_emails'
    )
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_for']
        verbose_name = 'Scheduled Email'
        verbose_name_plural = 'Scheduled Emails'
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['email_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.get_email_type_display()} ({self.scheduled_for})"
    
    def send(self):
        """Send the email"""
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        
        try:
            email = EmailMultiAlternatives(
                subject=self.subject,
                body=self.rendered_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.client.email]
            )
            
            if self.rendered_html:
                email.attach_alternative(self.rendered_html, "text/html")
            
            email.send()
            
            self.status = 'SENT'
            self.sent_at = timezone.now()
            self.save()
            
            return True
        except Exception as e:
            self.status = 'FAILED'
            self.error_message = str(e)
            self.save()
            return False


class EmailLog(models.Model):
    """Log all emails sent"""
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='email_logs'
    )
    
    subject = models.CharField(max_length=200)
    sent_to = models.EmailField()
    email_type = models.CharField(max_length=50)
    
    # References
    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    scheduled_email = models.ForeignKey(
        ScheduledEmail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    # Status
    sent_successfully = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        indexes = [
            models.Index(fields=['sent_at']),
            models.Index(fields=['client', 'email_type']),
        ]
    
    def __str__(self):
        return f"{self.subject} to {self.sent_to} on {self.sent_at}"
