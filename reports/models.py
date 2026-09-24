from django.db import models
from django.conf import settings


class Report(models.Model):
    """گزارش محتوا"""
    
    REASON_CHOICES = [
        ('spam', 'اسپم'),
        ('abuse', 'توهین و آزار'),
        ('inappropriate', 'محتوای نامناسب'),
        ('copyright', 'نقض حق تکثیر'),
        ('misinformation', 'اطلاعات نادرست'),
        ('other', 'دلیل دیگر'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('reviewed', 'بررسی‌شده'),
        ('resolved', 'حل‌شده'),
        ('rejected', 'رد‌شده'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('story', 'داستان'),
        ('segment', 'ادامه'),
        ('user', 'کاربر'),
    ]
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reports_made', verbose_name='گزارش‌دهنده'
    )
    
    content_type = models.CharField('نوع محتوا', max_length=20, choices=CONTENT_TYPE_CHOICES)
    reason = models.CharField('دلیل', max_length=20, choices=REASON_CHOICES)
    description = models.TextField('توضیحات', max_length=500, blank=True)
    
    # محتوای گزارش‌شده (فقط یکی از این‌ها پر می‌شه)
    story = models.ForeignKey(
        'stories.Story', on_delete=models.CASCADE,
        null=True, blank=True, related_name='reports'
    )
    segment = models.ForeignKey(
        'stories.Segment', on_delete=models.CASCADE,
        null=True, blank=True, related_name='reports'
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='reports_received'
    )
    
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField('یادداشت ادمین', blank=True)
    
    created_at = models.DateTimeField('تاریخ گزارش', auto_now_add=True)
    reviewed_at = models.DateTimeField('تاریخ بررسی', null=True, blank=True)

    class Meta:
        verbose_name = 'گزارش'
        verbose_name_plural = 'گزارش‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f'{self.reporter.username} - {self.get_content_type_display()} - {self.get_reason_display()}'

    @classmethod
    def create_story_report(cls, story, reporter, reason, description=''):
        return cls.objects.create(
            reporter=reporter,
            content_type='story',
            reason=reason,
            description=description,
            story=story,
        )

    @classmethod
    def create_segment_report(cls, segment, reporter, reason, description=''):
        return cls.objects.create(
            reporter=reporter,
            content_type='segment',
            reason=reason,
            description=description,
            segment=segment,
        )

    @classmethod
    def create_user_report(cls, reported_user, reporter, reason, description=''):
        return cls.objects.create(
            reporter=reporter,
            content_type='user',
            reason=reason,
            description=description,
            reported_user=reported_user,
        )