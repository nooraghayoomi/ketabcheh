from django.db import models
from django.conf import settings


class Notification(models.Model):
    """نوتیفیکیشن برای کاربر"""
    
    TYPE_CHOICES = [
        ('vote', 'رأی به ادامه‌ات'),
        ('canon', 'ادامه‌ات رسمی شد'),
        ('segment', 'ادامه جدید در داستانت'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='گیرنده'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_notifications', verbose_name='فرستنده',
        null=True, blank=True
    )
    
    notification_type = models.CharField('نوع', max_length=20, choices=TYPE_CHOICES)
    message = models.CharField('پیام', max_length=200)
    url = models.CharField('لینک', max_length=500, blank=True)
    
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)
    
    story = models.ForeignKey(
        'stories.Story', on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications'
    )
    segment = models.ForeignKey(
        'stories.Segment', on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications'
    )

    class Meta:
        verbose_name = 'نوتیفیکیشن'
        verbose_name_plural = 'نوتیفیکیشن‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.recipient.username} - {self.get_notification_type_display()}'

    @classmethod
    def create_vote_notification(cls, segment, voter):
        if segment.author == voter:
            return None
        return cls.objects.create(
            recipient=segment.author,
            sender=voter,
            notification_type='vote',
            message=f'{voter.username} به ادامه‌ات در «{segment.story.title}» رأی داد',
            url=f'{segment.story.get_absolute_url()}#segment-{segment.id}',
            story=segment.story,
            segment=segment,
        )

    @classmethod
    def create_canon_notification(cls, segment):
        if segment.author == segment.story.author:
            return None
        return cls.objects.create(
            recipient=segment.author,
            sender=segment.story.author,
            notification_type='canon',
            message=f'ادامه‌ات در «{segment.story.title}» به عنوان بخش رسمی انتخاب شد! ⭐',
            url=f'{segment.story.get_absolute_url()}#segment-{segment.id}',
            story=segment.story,
            segment=segment,
        )

    @classmethod
    def create_segment_notification(cls, segment):
        if segment.author == segment.story.author:
            return None
        return cls.objects.create(
            recipient=segment.story.author,
            sender=segment.author,
            notification_type='segment',
            message=f'{segment.author.username} به داستانت «{segment.story.title}» ادامه اضافه کرد',
            url=f'{segment.story.get_absolute_url()}#segment-{segment.id}',
            story=segment.story,
            segment=segment,
        )