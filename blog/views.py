from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.core.paginator import Paginator
from .models import Post


def post_list(request):
    """لیست همه پست‌ها"""
    posts = Post.objects.filter(status='published').select_related('author')
    
    paginator = Paginator(posts, 9)
    page = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'blog/post_list.html', {
        'page': page,
    })


def post_detail(request, slug):
    """صفحه یه پست"""
    post = get_object_or_404(
        Post.objects.select_related('author'),
        slug=slug,
        status='published'
    )
    
    # افزایش بازدید (فقط یه بار در هر نشست)
    session_key = f'viewed_post_{post.id}'
    if not request.session.get(session_key):
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
        request.session[session_key] = True
    
    # پست‌های مرتبط (بر اساس نویسنده)
    related_posts = Post.objects.filter(
        status='published',
        author=post.author
    ).exclude(pk=post.pk)[:3]
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })