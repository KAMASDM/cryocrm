from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Discount(models.Model):
    """Flexible discount system for packages and services"""
    
    DISCOUNT_TYPES = [
        ('PERCENTAGE', 'Percentage Off'),
        ('FIXED', 'Fixed Amount Off'),
        ('FREE_SESSION', 'Free Session(s)'),
        ('BOGO', 'Buy One Get One'),
    ]
    
    APPLIES_TO = [
        ('PACKAGE', 'Package'),
        ('SERVICE', 'Service'),
        ('ALL', 'All Purchases'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique discount code"
    )
    description = models.TextField()
    
    # Discount Configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO)
    
    # Discount Value
    percentage_off = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage discount (0-100)"
    )
    fixed_amount_off = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Fixed dollar amount off"
    )
    free_sessions = models.PositiveIntegerField(
        default=0,
        help_text="Number of free sessions"
    )
    
    # Applicable Items
    applicable_packages = models.ManyToManyField(
        'packages.Package',
        blank=True,
        related_name='discounts',
        help_text="Specific packages this discount applies to"
    )
    applicable_services = models.ManyToManyField(
        'services.Service',
        blank=True,
        related_name='discounts',
        help_text="Specific services this discount applies to"
    )
    
    # Validity
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Usage Limits
    max_uses_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum total uses (null = unlimited)"
    )
    max_uses_per_client = models.PositiveIntegerField(
        default=1,
        help_text="Maximum uses per client"
    )
    current_uses = models.PositiveIntegerField(default=0)
    
    # Minimum Requirements
    minimum_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum purchase amount required"
    )
    
    # Stackability
    can_be_combined = models.BooleanField(
        default=False,
        help_text="Can this discount be combined with other discounts?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_valid(self):
        """Check if discount is currently valid"""
        now = timezone.now().date()
        
        if not self.is_active:
            return False
        
        if now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        if self.max_uses_total and self.current_uses >= self.max_uses_total:
            return False
        
        return True
    
    def calculate_discount_amount(self, original_price):
        """Calculate the discount amount based on original price"""
        if self.discount_type == 'PERCENTAGE' and self.percentage_off:
            return original_price * (self.percentage_off / 100)
        elif self.discount_type == 'FIXED' and self.fixed_amount_off:
            return min(self.fixed_amount_off, original_price)
        return Decimal('0.00')
    
    def can_client_use(self, client):
        """Check if a specific client can use this discount"""
        if not self.is_valid():
            return False
        
        # Check client usage
        client_usage = DiscountUsage.objects.filter(
            discount=self,
            client=client
        ).count()
        
        return client_usage < self.max_uses_per_client


class DiscountUsage(models.Model):
    """Track discount usage"""
    
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='discount_usages'
    )
    
    # What was purchased
    package_purchase = models.ForeignKey(
        'packages.PackagePurchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='discount_usages'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='discount_usages'
    )
    
    # Discount details
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount discounted"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Original price before discount"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final price after discount"
    )
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Discount Usage'
        verbose_name_plural = 'Discount Usages'
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.discount.code}"


class Referral(models.Model):
    """Track referral program"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REWARDED', 'Rewarded'),
    ]
    
    referrer = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='referrals_made',
        help_text="Client who made the referral"
    )
    referred_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='referral_received',
        help_text="Client who was referred"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Reward details
    referrer_discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrer_rewards',
        help_text="Discount given to referrer"
    )
    referred_discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_rewards',
        help_text="Discount given to referred client"
    )
    
    referral_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(null=True, blank=True)
    rewarded_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-referral_date']
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = ['referrer', 'referred_client']
    
    def __str__(self):
        return f"{self.referrer.get_full_name()} referred {self.referred_client.get_full_name()}"
    
    def mark_completed(self):
        """Mark referral as completed when referred client makes first purchase"""
        if self.status == 'PENDING':
            self.status = 'COMPLETED'
            self.completed_date = timezone.now().date()
            self.save()
    
    def mark_rewarded(self):
        """Mark referral as rewarded"""
        if self.status == 'COMPLETED':
            self.status = 'REWARDED'
            self.rewarded_date = timezone.now().date()
            self.save()
