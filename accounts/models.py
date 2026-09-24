from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """کاربر سفارشی کتابچه"""
    
    bio = models.TextField('درباره من', max_length=500, blank=True)
    avatar = models.ImageField('آواتار', upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField('تاریخ تولد', blank=True, null=True)
    
    total_stories = models.PositiveIntegerField('تعداد داستان‌ها', default=0)
    total_continuations = models.PositiveIntegerField('تعداد ادامه‌ها', default=0)
    total_votes_received = models.PositiveIntegerField('رأی‌های دریافتی', default=0)
    
    favorite_genre = models.CharField('ژانر محبوب', max_length=50, blank=True)
    email_verified = models.BooleanField('ایمیل تأیید شده', default=False)
    
    created_at = models.DateTimeField('تاریخ عضویت', auto_now_add=True)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username

    def get_display_name(self):
        return self.get_full_name() or self.username