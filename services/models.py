from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ServiceType(models.Model):
    """Master table for service types/categories"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Unique code for this service type")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Order for display in lists")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """Individual service offered by the wellness center"""
    
    name = models.CharField(max_length=200)
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.PROTECT,
        related_name='services',
        help_text="Category/type of this service"
    )
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Default duration in minutes"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Base price per session"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for service configuration
    preparation_instructions = models.TextField(
        blank=True,
        help_text="Instructions for clients before the session"
    )
    contraindications = models.TextField(
        blank=True,
        help_text="Medical contraindications or warnings"
    )
    benefits = models.TextField(
        blank=True,
        help_text="Key benefits of this service"
    )
    
    class Meta:
        ordering = ['service_type__display_order', 'name']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def __str__(self):
        return f"{self.name} ({self.service_type.name})"
    
    def get_price_with_currency(self):
        return f"${self.base_price}"
    get_price_with_currency.short_description = "Price"
