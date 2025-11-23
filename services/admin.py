from django.contrib import admin
from .models import Service, ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'service_type', 
        'duration_minutes', 
        'get_price_with_currency',
        'is_active',
        'created_at'
    ]
    list_filter = ['service_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'benefits']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'service_type', 'description', 'is_active')
        }),
        ('Pricing & Duration', {
            'fields': ('base_price', 'duration_minutes')
        }),
        ('Service Details', {
            'fields': ('benefits', 'preparation_instructions', 'contraindications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
