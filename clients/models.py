from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Client(models.Model):
    """Client/Customer information"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()]
    )
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='USA')
    
    # Medical Information
    medical_conditions = models.TextField(
        blank=True,
        help_text="Any relevant medical conditions or health concerns"
    )
    medications = models.TextField(
        blank=True,
        help_text="Current medications"
    )
    allergies = models.TextField(
        blank=True,
        help_text="Known allergies"
    )
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Client Status
    is_active = models.BooleanField(default=True)
    registration_date = models.DateField(auto_now_add=True)
    last_visit_date = models.DateField(null=True, blank=True)
    
    # Marketing Preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive appointment reminders and updates"
    )
    marketing_emails = models.BooleanField(
        default=True,
        help_text="Receive promotional offers and newsletters"
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text="Receive SMS notifications"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the client"
    )
    
    # Referral tracking
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        help_text="Who referred this client"
    )
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique referral code for this client"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def get_total_appointments(self):
        return self.appointments.count()
    
    def get_completed_appointments(self):
        return self.appointments.filter(status='COMPLETED').count()
    
    def get_active_packages(self):
        return self.package_purchases.filter(status='ACTIVE')
    
    def get_lifetime_value(self):
        """Calculate total revenue from this client"""
        from django.db.models import Sum
        from decimal import Decimal
        
        # Sum from package purchases
        package_total = self.package_purchases.aggregate(
            total=Sum('final_price')
        )['total'] or Decimal('0.00')
        
        # Sum from individual appointments
        appointment_total = self.appointments.filter(
            status='COMPLETED'
        ).aggregate(
            total=Sum('final_price')
        )['total'] or Decimal('0.00')
        
        return package_total + appointment_total
    
    def save(self, *args, **kwargs):
        # Generate referral code if not exists
        if not self.referral_code:
            import random
            import string
            self.referral_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        super().save(*args, **kwargs)
