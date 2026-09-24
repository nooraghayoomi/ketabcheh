from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField('نام ژانر', max_length=50, unique=True)
    slug = models.SlugField('اسلاگ', max_length=60, unique=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True, max_length=300)
    color = models.CharField('رنگ', max_length=20, default='#D4A574')

    class Meta:
        verbose_name = 'ژانر'
        verbose_name_plural = 'ژانرها'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Story(models.Model):
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('active', 'فعال'),
        ('completed', 'تمام‌شده'),
        ('archived', 'بایگانی'),
    ]

    title = models.CharField('عنوان', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=220, unique=True, allow_unicode=True, blank=True)
    description = models.TextField('خلاصه', max_length=500, blank=True)

    cover = models.ImageField('کاور', upload_to='covers/', blank=True, null=True)
    
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, 
                              related_name='stories', verbose_name='ژانر')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='stories', verbose_name='نویسنده')
    
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField('ویژه', default=False)
    
    total_segments = models.PositiveIntegerField('تعداد ادامه‌ها', default=0)
    total_votes = models.PositiveIntegerField('کل رأی‌ها', default=0)
    total_views = models.PositiveIntegerField('بازدیدها', default=0)
    
    created_at = models.DateTimeField('تاریخ ساخت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'داستان'
        verbose_name_plural = 'داستان‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = 'story'
            slug = base_slug
            counter = 1
            while Story.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('stories:detail', kwargs={'slug': self.slug})


class Segment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE,
                              related_name='segments', verbose_name='داستان')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='ادامه قبلی')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='segments', verbose_name='نویسنده')
    
    text = models.TextField('متن', max_length=2000)
    
    votes = models.IntegerField('رأی‌ها', default=0)
    is_canon = models.BooleanField('ادامه رسمی', default=False)
    
    created_at = models.DateTimeField('تاریخ نوشتن', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'ادامه'
        verbose_name_plural = 'ادامه‌ها'
        ordering = ['-votes', 'created_at']
        indexes = [
            models.Index(fields=['story', 'is_canon']),
            models.Index(fields=['story', 'parent']),
        ]

    def __str__(self):
        return f'{self.story.title} - {self.text[:40]}...'


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='votes', verbose_name='کاربر')
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE,
                                related_name='vote_records', verbose_name='ادامه')
    created_at = models.DateTimeField('تاریخ رأی', auto_now_add=True)

    class Meta:
        verbose_name = 'رأی'
        verbose_name_plural = 'رأی‌ها'
        unique_together = ('user', 'segment')

    def __str__(self):
        return f'{self.user.username} → {self.segment.id}'