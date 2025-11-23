from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Appointment(models.Model):
    """Client appointments for services"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    # Client and Service
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        related_name='appointments'
    )
    
    # Package tracking (if appointment is part of a package)
    package_purchase = models.ForeignKey(
        'packages.PackagePurchase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        help_text="Package this appointment is booked from"
    )
    
    # Scheduling
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    end_time = models.TimeField(editable=False, null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    
    # Pricing (for non-package appointments)
    service_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Notes and feedback
    notes = models.TextField(
        blank=True,
        help_text="Appointment notes or special requests"
    )
    therapist_notes = models.TextField(
        blank=True,
        help_text="Notes from the therapist/staff"
    )
    client_feedback = models.TextField(
        blank=True,
        help_text="Client feedback after session"
    )
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MinValueValidator(5)],
        help_text="Client rating (1-5)"
    )
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        indexes = [
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} on {self.appointment_date}"
    
    def save(self, *args, **kwargs):
        # Calculate end time
        if self.appointment_time and self.duration_minutes:
            from datetime import datetime, timedelta
            start_datetime = datetime.combine(
                self.appointment_date,
                self.appointment_time
            )
            end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
            self.end_time = end_datetime.time()
        
        # Set service price if not set
        if not self.service_price:
            self.service_price = self.service.base_price
        
        # Calculate final price
        if self.package_purchase:
            # If from package, it's essentially free (already paid)
            self.final_price = Decimal('0.00')
        else:
            self.final_price = self.service_price - self.discount_amount
        
        # Set completed timestamp
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Update client's last visit date
        if self.status == 'COMPLETED':
            self.client.last_visit_date = self.appointment_date
            self.client.save()
        
        super().save(*args, **kwargs)
        
        # Update package usage if applicable
        if self.package_purchase and self.status == 'COMPLETED':
            if self.package_purchase.sessions_used < self.package_purchase.total_sessions:
                self.package_purchase.sessions_used += 1
                self.package_purchase.save()
    
    def is_upcoming(self):
        """Check if appointment is in the future"""
        from datetime import datetime
        appointment_datetime = datetime.combine(
            self.appointment_date,
            self.appointment_time
        )
        return appointment_datetime > timezone.now()
    
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status in ['SCHEDULED', 'CONFIRMED'] and self.is_upcoming()


class AppointmentHistory(models.Model):
    """Track appointment status changes"""
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Appointment History'
        verbose_name_plural = 'Appointment Histories'
    
    def __str__(self):
        return f"{self.appointment} - {self.previous_status} to {self.new_status}"
