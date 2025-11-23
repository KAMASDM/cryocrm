from django.contrib import admin
from django.utils.html import format_html
from .models import Package, PackagePurchase


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'total_sessions',
        'session_frequency',
        'price',
        'validity_days',
        'is_active'
    ]
    list_filter = ['category', 'is_active', 'can_combine_services']
    search_fields = ['name', 'description', 'benefits']
    filter_horizontal = ['services']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Package Information', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Services', {
            'fields': ('services', 'can_combine_services')
        }),
        ('Session Requirements', {
            'fields': (
                'total_sessions',
                'min_sessions_per_week',
                'max_sessions_per_week',
                'validity_days'
            )
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Additional Information', {
            'fields': ('benefits', 'terms_and_conditions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def session_frequency(self, obj):
        return f"{obj.min_sessions_per_week}-{obj.max_sessions_per_week} per week"
    session_frequency.short_description = "Frequency"


@admin.register(PackagePurchase)
class PackagePurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'client',
        'package',
        'purchase_date',
        'expiry_date',
        'status',
        'session_progress',
        'final_price'
    ]
    list_filter = ['status', 'purchase_date', 'expiry_date']
    search_fields = [
        'client__first_name',
        'client__last_name',
        'client__email',
        'package__name'
    ]
    readonly_fields = [
        'purchase_date',
        'sessions_remaining',
        'created_at',
        'updated_at',
        'get_usage_percentage'
    ]
    autocomplete_fields = ['client', 'package']
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('client', 'package', 'status')
        }),
        ('Dates', {
            'fields': ('purchase_date', 'expiry_date')
        }),
        ('Pricing', {
            'fields': ('original_price', 'discount_applied', 'final_price')
        }),
        ('Session Tracking', {
            'fields': (
                'total_sessions',
                'sessions_used',
                'sessions_remaining',
                'get_usage_percentage'
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
    
    def session_progress(self, obj):
        percentage = obj.get_usage_percentage()
        color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.sessions_used,
            obj.total_sessions,
            round(percentage, 1)
        )
    session_progress.short_description = "Sessions Used"
    
    def save_model(self, request, obj, form, change):
        # Set initial values if creating new purchase
        if not change:
            obj.original_price = obj.package.price
            obj.total_sessions = obj.package.total_sessions
            if obj.discount_applied is None:
                obj.discount_applied = 0
            obj.final_price = obj.original_price - obj.discount_applied
        super().save_model(request, obj, form, change)
