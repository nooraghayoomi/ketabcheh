from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    """پست وبلاگ"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    ]
    
    title = models.CharField('عنوان', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=220, unique=True, allow_unicode=True, blank=True)
    excerpt = models.TextField('خلاصه', max_length=300, blank=True, 
                                help_text='خلاصه‌ای که توی لیست پست‌ها نشون داده می‌شه')
    content = models.TextField('محتوا')
    cover = models.ImageField('کاور', upload_to='blog/covers/', blank=True, null=True)
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='blog_posts', verbose_name='نویسنده')
    
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('ویژه', default=False)
    
    views = models.PositiveIntegerField('بازدید', default=0)
    
    created_at = models.DateTimeField('تاریخ ساخت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)
    published_at = models.DateTimeField('تاریخ انتشار', blank=True, null=True)

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = 'پست‌ها'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        
        # اگه منتشر شد و تاریخ انتشار نداره
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def reading_time(self):
        """زمان تقریبی مطالعه (به دقیقه)"""
        words = len(self.content.split())
        return max(1, words // 200)