from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from services.models import Service


class Package(models.Model):
    """Treatment packages combining multiple services"""
    
    PACKAGE_CATEGORIES = [
        ('ENERGY', 'Fatigue / Focus / Energy'),
        ('PAIN', 'Pain and Inflammation'),
        ('INJURY', 'Injury Recovery and Prevention'),
        ('BEAUTY', 'Beauty and Skin Health'),
        ('WELLNESS', 'Wellbeing and Stress Relief'),
        ('CUSTOM', 'Custom Package'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES)
    description = models.TextField()
    services = models.ManyToManyField(
        Service,
        related_name='packages',
        help_text="Services included in this package"
    )
    
    # Session requirements
    total_sessions = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of sessions in the package"
    )
    min_sessions_per_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Minimum sessions per week recommended"
    )
    max_sessions_per_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum sessions per week recommended"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total package price"
    )
    
    # Validity
    validity_days = models.PositiveIntegerField(
        default=90,
        help_text="Number of days the package is valid from purchase"
    )
    
    # Features
    can_combine_services = models.BooleanField(
        default=False,
        help_text="Can multiple services be used in the same visit?"
    )
    is_sharable = models.BooleanField(
        default=False,
        help_text="Can this package be shared with family/friends?"
    )
    is_active = models.BooleanField(default=True)
    
    # Benefits and notes
    benefits = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'
    
    def __str__(self):
        return f"{self.name} ({self.total_sessions} sessions)"
    
    def get_price_per_session(self):
        if self.total_sessions > 0:
            return self.price / self.total_sessions
        return Decimal('0.00')
    
    def get_service_names(self):
        return ", ".join([s.name for s in self.services.all()])
    get_service_names.short_description = "Services"


class PackagePurchase(models.Model):
    """Track client purchases of packages"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='package_purchases'
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name='purchases'
    )
    
    # Purchase details
    purchase_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Pricing
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Original package price"
    )
    discount_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total discount amount"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final price paid"
    )
    
    # Session tracking
    total_sessions = models.PositiveIntegerField()
    sessions_used = models.PositiveIntegerField(default=0)
    sessions_remaining = models.PositiveIntegerField()
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Package Purchase'
        verbose_name_plural = 'Package Purchases'
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.package.name}"
    
    def save(self, *args, **kwargs):
        # Set expiry date based on package validity
        if not self.expiry_date and self.package:
            from datetime import timedelta
            self.expiry_date = self.purchase_date + timedelta(days=self.package.validity_days)
        
        # Calculate sessions remaining
        self.sessions_remaining = self.total_sessions - self.sessions_used
        
        # Update status based on sessions and expiry
        if self.sessions_remaining <= 0:
            self.status = 'COMPLETED'
        elif self.expiry_date:
            from django.utils import timezone
            if timezone.now().date() > self.expiry_date:
                self.status = 'EXPIRED'
        
        super().save(*args, **kwargs)
    
    def get_usage_percentage(self):
        if self.total_sessions > 0:
            return (self.sessions_used / self.total_sessions) * 100
        return 0
    
    def can_book_session(self):
        """Check if client can book another session from this package"""
        from django.utils import timezone
        return (
            self.status == 'ACTIVE' and
            self.sessions_remaining > 0 and
            self.expiry_date >= timezone.now().date()
        )
