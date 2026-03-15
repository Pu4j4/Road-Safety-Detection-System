from django.contrib import admin
from django.utils.html import format_html
from .models import DetectionRecord, AlertLog


class AlertLogInline(admin.TabularInline):
    model = AlertLog
    extra = 0
    readonly_fields = ['phone_number', 'message_sid', 'message_body', 'success', 'error_message', 'sent_at']
    can_delete = False


@admin.register(DetectionRecord)
class DetectionRecordAdmin(admin.ModelAdmin):
    list_display  = ['id', 'detection_type', 'media_type', 'status_badge', 'pothole_count', 'alert_sent', 'processing_time_display', 'created_at']
    list_filter   = ['detection_type', 'media_type', 'status', 'alert_sent', 'created_at']
    search_fields = ['id', 'error_message']
    readonly_fields = ['status', 'pothole_count', 'pothole_detected', 'alert_sent',
                       'alert_sent_at', 'processing_time_ms', 'error_message',
                       'created_at', 'updated_at', 'result_file']
    inlines = [AlertLogInline]
    ordering = ['-created_at']

    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'processing': '#3b82f6', 'completed': '#10b981', 'failed': '#ef4444'}
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def processing_time_display(self, obj):
        return f"{obj.processing_time_ms:.0f} ms" if obj.processing_time_ms else '-'
    processing_time_display.short_description = 'Time'


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display  = ['id', 'detection', 'phone_number', 'success', 'message_sid', 'sent_at']
    list_filter   = ['success', 'sent_at']
    readonly_fields = ['detection', 'phone_number', 'message_sid', 'message_body', 'success', 'error_message', 'sent_at']


admin.site.site_header = "🚗 Road Safety Detection System"
admin.site.site_title  = "Road Safety Detection System"
admin.site.index_title = "Detection Management"
