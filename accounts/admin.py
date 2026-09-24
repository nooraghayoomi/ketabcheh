from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'total_stories', 'total_continuations', 'created_at', 'is_active')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات اضافی', {'fields': ('bio', 'avatar', 'birth_date', 'favorite_genre')}),
        ('آمار', {'fields': ('total_stories', 'total_continuations', 'total_votes_received')}),
        ('وضعیت', {'fields': ('email_verified',)}),
    )