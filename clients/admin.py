from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name',
        'email',
        'phone',
        'is_active',
        'registration_date',
        'last_visit_date',
        'get_total_appointments',
        'get_lifetime_value'
    ]
    list_filter = [
        'is_active',
        'gender',
        'registration_date',
        'marketing_emails',
        'email_notifications'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'referral_code'
    ]
    readonly_fields = [
        'registration_date',
        'referral_code',
        'created_at',
        'updated_at',
        'get_age',
        'get_total_appointments',
        'get_completed_appointments',
        'get_lifetime_value'
    ]
    autocomplete_fields = ['referred_by']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'date_of_birth',
                'get_age',
                'gender'
            )
        }),
        ('Address', {
            'fields': (
                'address_line1',
                'address_line2',
                'city',
                'state',
                'zip_code',
                'country'
            ),
            'classes': ('collapse',)
        }),
        ('Medical Information', {
            'fields': (
                'medical_conditions',
                'medications',
                'allergies',
                'emergency_contact_name',
                'emergency_contact_phone'
            ),
            'classes': ('collapse',)
        }),
        ('Client Status', {
            'fields': (
                'is_active',
                'registration_date',
                'last_visit_date',
                'get_total_appointments',
                'get_completed_appointments',
                'get_lifetime_value'
            )
        }),
        ('Communication Preferences', {
            'fields': (
                'email_notifications',
                'marketing_emails',
                'sms_notifications'
            )
        }),
        ('Referral Information', {
            'fields': (
                'referred_by',
                'referral_code'
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('referred_by')
