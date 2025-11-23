from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import EmailTemplate, EmailCampaign, ScheduledEmail, EmailLog


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'template_type',
        'subject',
        'is_active',
        'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'html_content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Variables', {
            'fields': ('available_variables',),
            'description': 'Available variables: client_name, client_email, appointment_date, appointment_time, service_name, package_name, expiry_date, etc.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'template',
        'status',
        'scheduled_for',
        'campaign_stats',
        'created_at'
    ]
    list_filter = ['status', 'scheduled_for', 'created_at']
    search_fields = ['name', 'template__name']
    filter_horizontal = ['target_clients']
    readonly_fields = [
        'total_recipients',
        'emails_sent',
        'emails_failed',
        'emails_opened',
        'links_clicked',
        'sent_at',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'template', 'status')
        }),
        ('Targeting', {
            'fields': (
                'send_to_all',
                'target_clients',
                'only_marketing_subscribers',
                'only_active_clients'
            )
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'sent_at')
        }),
        ('Statistics', {
            'fields': (
                'total_recipients',
                'emails_sent',
                'emails_failed',
                'emails_opened',
                'links_clicked'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_campaign', 'cancel_campaign']
    
    def campaign_stats(self, obj):
        if obj.emails_sent > 0:
            open_rate = (obj.emails_opened / obj.emails_sent) * 100 if obj.emails_sent else 0
            click_rate = (obj.links_clicked / obj.emails_sent) * 100 if obj.emails_sent else 0
            return format_html(
                'Sent: {} | Opened: {} ({:.1f}%) | Clicked: {} ({:.1f}%)',
                obj.emails_sent,
                obj.emails_opened,
                open_rate,
                obj.links_clicked,
                click_rate
            )
        return "Not sent yet"
    campaign_stats.short_description = "Campaign Stats"
    
    def send_campaign(self, request, queryset):
        from .tasks import send_email_campaign
        count = 0
        for campaign in queryset.filter(status='SCHEDULED'):
            send_email_campaign(campaign.id)
            count += 1
        self.message_user(request, f"{count} campaigns are being sent.")
    send_campaign.short_description = "Send selected campaigns now"
    
    def cancel_campaign(self, request, queryset):
        queryset.filter(status__in=['DRAFT', 'SCHEDULED']).update(status='CANCELLED')
        self.message_user(request, f"{queryset.count()} campaigns cancelled.")
    cancel_campaign.short_description = "Cancel selected campaigns"


@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = [
        'client',
        'email_type',
        'subject',
        'scheduled_for',
        'status',
        'sent_at'
    ]
    list_filter = [
        'email_type',
        'status',
        'scheduled_for',
        'sent_at'
    ]
    search_fields = [
        'client__first_name',
        'client__last_name',
        'subject'
    ]
    readonly_fields = [
        'sent_at',
        'opened_at',
        'created_at',
        'updated_at',
        'error_message'
    ]
    autocomplete_fields = ['client', 'template', 'appointment', 'package_purchase']
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Email Information', {
            'fields': ('client', 'email_type', 'template', 'status')
        }),
        ('Content', {
            'fields': ('subject', 'rendered_html', 'rendered_text')
        }),
        ('Related Objects', {
            'fields': ('appointment', 'package_purchase'),
            'classes': ('collapse',)
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'sent_at', 'opened_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_now', 'cancel_emails']
    
    def send_now(self, request, queryset):
        count = 0
        for email in queryset.filter(status='PENDING'):
            if email.send():
                count += 1
        self.message_user(request, f"{count} emails sent successfully.")
    send_now.short_description = "Send selected emails now"
    
    def cancel_emails(self, request, queryset):
        queryset.filter(status='PENDING').update(status='CANCELLED')
        self.message_user(request, f"{queryset.count()} emails cancelled.")
    cancel_emails.short_description = "Cancel selected emails"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'client',
        'subject',
        'email_type',
        'sent_successfully',
        'sent_at',
        'opened_at'
    ]
    list_filter = [
        'email_type',
        'sent_successfully',
        'sent_at'
    ]
    search_fields = [
        'client__first_name',
        'client__last_name',
        'subject',
        'sent_to'
    ]
    readonly_fields = [
        'client',
        'subject',
        'sent_to',
        'email_type',
        'campaign',
        'scheduled_email',
        'sent_successfully',
        'error_message',
        'sent_at',
        'opened_at',
        'clicked_at'
    ]
    date_hierarchy = 'sent_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
