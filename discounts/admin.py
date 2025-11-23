from django.contrib import admin
from django.utils.html import format_html
from .models import Discount, DiscountUsage, Referral


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'discount_type',
        'get_discount_value',
        'applies_to',
        'is_active',
        'is_valid',
        'usage_stats',
        'start_date',
        'end_date'
    ]
    list_filter = [
        'discount_type',
        'applies_to',
        'is_active',
        'start_date',
        'end_date',
        'can_be_combined'
    ]
    search_fields = ['name', 'code', 'description']
    filter_horizontal = ['applicable_packages', 'applicable_services']
    readonly_fields = ['current_uses', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Discount Configuration', {
            'fields': (
                'discount_type',
                'applies_to',
                'percentage_off',
                'fixed_amount_off',
                'free_sessions'
            )
        }),
        ('Applicable Items', {
            'fields': ('applicable_packages', 'applicable_services'),
            'classes': ('collapse',)
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Usage Limits', {
            'fields': (
                'max_uses_total',
                'max_uses_per_client',
                'current_uses',
                'minimum_purchase_amount'
            )
        }),
        ('Advanced Options', {
            'fields': ('can_be_combined',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_discount_value(self, obj):
        if obj.discount_type == 'PERCENTAGE':
            return f"{obj.percentage_off}%"
        elif obj.discount_type == 'FIXED':
            return f"${obj.fixed_amount_off}"
        elif obj.discount_type == 'FREE_SESSION':
            return f"{obj.free_sessions} free sessions"
        return "N/A"
    get_discount_value.short_description = "Value"
    
    def usage_stats(self, obj):
        if obj.max_uses_total:
            percentage = (obj.current_uses / obj.max_uses_total) * 100
            color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
            return format_html(
                '<span style="color: {};">{}/{} ({}%)</span>',
                color,
                obj.current_uses,
                obj.max_uses_total,
                round(percentage, 1)
            )
        return f"{obj.current_uses} uses"
    usage_stats.short_description = "Usage"


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = [
        'client',
        'discount',
        'original_price',
        'discount_amount',
        'final_price',
        'used_at'
    ]
    list_filter = ['used_at', 'discount']
    search_fields = [
        'client__first_name',
        'client__last_name',
        'discount__code',
        'discount__name'
    ]
    readonly_fields = ['used_at']
    autocomplete_fields = ['client', 'discount']
    
    def has_add_permission(self, request):
        # Usage is typically created automatically
        return False


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = [
        'referrer',
        'referred_client',
        'status',
        'referral_date',
        'completed_date',
        'rewarded_date'
    ]
    list_filter = ['status', 'referral_date', 'completed_date']
    search_fields = [
        'referrer__first_name',
        'referrer__last_name',
        'referred_client__first_name',
        'referred_client__last_name'
    ]
    readonly_fields = ['referral_date', 'completed_date', 'rewarded_date']
    autocomplete_fields = ['referrer', 'referred_client', 'referrer_discount', 'referred_discount']
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referrer', 'referred_client', 'status')
        }),
        ('Rewards', {
            'fields': ('referrer_discount', 'referred_discount')
        }),
        ('Dates', {
            'fields': ('referral_date', 'completed_date', 'rewarded_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_rewarded']
    
    def mark_as_completed(self, request, queryset):
        for referral in queryset.filter(status='PENDING'):
            referral.mark_completed()
        self.message_user(request, f"{queryset.count()} referrals marked as completed.")
    mark_as_completed.short_description = "Mark selected as completed"
    
    def mark_as_rewarded(self, request, queryset):
        for referral in queryset.filter(status='COMPLETED'):
            referral.mark_rewarded()
        self.message_user(request, f"{queryset.count()} referrals marked as rewarded.")
    mark_as_rewarded.short_description = "Mark selected as rewarded"
