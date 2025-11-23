from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Appointment, AppointmentHistory


class AppointmentHistoryInline(admin.TabularInline):
    model = AppointmentHistory
    extra = 0
    readonly_fields = ['previous_status', 'new_status', 'changed_by', 'changed_at', 'notes']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'client',
        'service',
        'appointment_date',
        'appointment_time',
        'duration_minutes',
        'status',
        'final_price',
        'get_package_info',
        'reminder_sent'
    ]
    list_filter = [
        'status',
        'appointment_date',
        'service',
        'reminder_sent'
    ]
    search_fields = [
        'client__first_name',
        'client__last_name',
        'client__email',
        'service__name'
    ]
    readonly_fields = [
        'end_time',
        'created_at',
        'updated_at',
        'completed_at',
        'reminder_sent_at'
    ]
    autocomplete_fields = ['client', 'service', 'package_purchase']
    date_hierarchy = 'appointment_date'
    inlines = [AppointmentHistoryInline]
    
    fieldsets = (
        ('Appointment Details', {
            'fields': (
                'client',
                'service',
                'package_purchase',
                'status'
            )
        }),
        ('Schedule', {
            'fields': (
                'appointment_date',
                'appointment_time',
                'duration_minutes',
                'end_time'
            )
        }),
        ('Pricing', {
            'fields': (
                'service_price',
                'discount_amount',
                'final_price'
            )
        }),
        ('Notes & Feedback', {
            'fields': (
                'notes',
                'therapist_notes',
                'client_feedback',
                'rating'
            ),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': (
                'reminder_sent',
                'reminder_sent_at'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_confirmed',
        'mark_as_completed',
        'mark_as_cancelled',
        'send_reminders'
    ]
    
    def get_package_info(self, obj):
        if obj.package_purchase:
            return format_html(
                '<span style="color: green;">✓ Package</span>'
            )
        return format_html('<span style="color: gray;">Individual</span>')
    get_package_info.short_description = "Type"
    
    def mark_as_confirmed(self, request, queryset):
        queryset.filter(status='SCHEDULED').update(status='CONFIRMED')
        self.message_user(request, f"{queryset.count()} appointments confirmed.")
    mark_as_confirmed.short_description = "Mark as confirmed"
    
    def mark_as_completed(self, request, queryset):
        for appointment in queryset:
            if appointment.status not in ['COMPLETED', 'CANCELLED']:
                appointment.status = 'COMPLETED'
                appointment.save()
        self.message_user(request, f"{queryset.count()} appointments completed.")
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, f"{queryset.count()} appointments cancelled.")
    mark_as_cancelled.short_description = "Mark as cancelled"
    
    def send_reminders(self, request, queryset):
        from communications.tasks import send_appointment_reminder
        count = 0
        for appointment in queryset.filter(
            status__in=['SCHEDULED', 'CONFIRMED'],
            reminder_sent=False
        ):
            if appointment.is_upcoming():
                send_appointment_reminder(appointment.id)
                count += 1
        self.message_user(request, f"{count} reminders sent.")
    send_reminders.short_description = "Send appointment reminders"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'service', 'package_purchase')


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'appointment',
        'previous_status',
        'new_status',
        'changed_by',
        'changed_at'
    ]
    list_filter = ['previous_status', 'new_status', 'changed_at']
    search_fields = [
        'appointment__client__first_name',
        'appointment__client__last_name'
    ]
    readonly_fields = [
        'appointment',
        'previous_status',
        'new_status',
        'changed_by',
        'changed_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
