from django.contrib import admin
from django.utils import timezone
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'content_type', 'reason', 'status', 'created_at')
    list_filter = ('content_type', 'reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'description', 'admin_note')
    raw_id_fields = ('reporter', 'story', 'segment', 'reported_user')
    date_hierarchy = 'created_at'
    readonly_fields = ('reporter', 'content_type', 'reason', 'description', 'story', 'segment', 'reported_user', 'created_at')
    
    fieldsets = (
        ('اطلاعات گزارش', {
            'fields': ('reporter', 'content_type', 'reason', 'description', 'created_at')
        }),
        ('محتوای گزارش‌شده', {
            'fields': ('story', 'segment', 'reported_user')
        }),
        ('بررسی', {
            'fields': ('status', 'admin_note', 'reviewed_at')
        }),
    )
    
    actions = ['mark_resolved', 'mark_rejected']
    
    @admin.action(description='علامت‌گذاری به عنوان حل‌شده')
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved', reviewed_at=timezone.now())
    
    @admin.action(description='رد گزارش')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected', reviewed_at=timezone.now())
    
    def save_model(self, request, obj, form, change):
        if obj.status != 'pending' and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)