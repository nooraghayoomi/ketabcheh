from django.shortcuts import render
from stories.models import Story, Genre, Segment


def home_view(request):
    """صفحه اصلی با داستان‌های واقعی"""
    
    featured_story = Story.objects.filter(
        status='active', is_featured=True
    ).select_related('author', 'genre').first()
    
    if not featured_story:
        featured_story = Story.objects.filter(
            status='active'
        ).select_related('author', 'genre').order_by('-total_votes').first()
    
    hot_stories = Story.objects.filter(
        status='active'
    ).exclude(pk=featured_story.pk if featured_story else 0
    ).select_related('author', 'genre').order_by('-total_votes', '-created_at')[:6]
    
    new_stories = Story.objects.filter(
        status='active'
    ).select_related('author', 'genre').order_by('-created_at')[:3]
    
    stats = {
        'total_stories': Story.objects.filter(status='active').count(),
        'total_segments': Segment.objects.count(),
        'total_writers': Story.objects.values('author').distinct().count(),
    }
    
    genres = Genre.objects.all()[:6]
    
    return render(request, 'home.html', {
        'featured_story': featured_story,
        'hot_stories': hot_stories,
        'new_stories': new_stories,
        'stats': stats,
        'genres': genres,
    })