from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'is_featured', 'views', 'published_at')
    list_filter = ('status', 'is_featured', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ('status', 'is_featured')
    readonly_fields = ('author', 'views', 'created_at', 'updated_at', 'published_at')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'cover')
        }),
        ('انتشار', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('author', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """نویسنده رو خودکار ست کن"""
        if not change:  # فقط وقتی پست جدید ساخته می‌شه
            obj.author = request.user
        super().save_model(request, obj, form, change)