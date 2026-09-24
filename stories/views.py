from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Story, Segment, Vote, Genre
from .forms import StoryForm, SegmentForm
from notifications.models import Notification


def story_list(request):
    """لیست همه داستان‌ها"""
    stories = Story.objects.filter(status='active').select_related('author', 'genre')
    
    genre_slug = request.GET.get('genre')
    if genre_slug:
        stories = stories.filter(genre__slug=genre_slug)
    
    sort = request.GET.get('sort', 'new')
    if sort == 'hot':
        stories = stories.order_by('-total_votes', '-created_at')
    elif sort == 'views':
        stories = stories.order_by('-total_views')
    else:
        stories = stories.order_by('-created_at')
    
    paginator = Paginator(stories, 9)
    page = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'stories/story_list.html', {
        'page': page,
        'genres': Genre.objects.all(),
        'current_genre': genre_slug,
        'current_sort': sort,
    })


def story_detail(request, slug):
    """صفحه یه داستان + ادامه‌ها"""
    story = get_object_or_404(Story.objects.select_related('author', 'genre'), slug=slug)
    
    session_key = f'viewed_story_{story.id}'
    if not request.session.get(session_key):
        Story.objects.filter(pk=story.pk).update(total_views=F('total_views') + 1)
        request.session[session_key] = True
    
    canon_segments = story.segments.filter(is_canon=True).order_by('created_at')
    last_canon = canon_segments.last()
    
    if last_canon:
        suggestions = story.segments.filter(parent=last_canon, is_canon=False).order_by('-votes', '-created_at')[:10]
    else:
        suggestions = story.segments.filter(parent__isnull=True, is_canon=False).order_by('-votes', '-created_at')[:10]
    
    user_votes = set()
    if request.user.is_authenticated:
        user_votes = set(
            Vote.objects.filter(user=request.user, segment__story=story)
            .values_list('segment_id', flat=True)
        )
    
    segment_form = SegmentForm()
    
    return render(request, 'stories/story_detail.html', {
        'story': story,
        'canon_segments': canon_segments,
        'suggestions': suggestions,
        'user_votes': user_votes,
        'segment_form': segment_form,
        'last_canon': last_canon,
    })


@login_required
def count_letters(text):
    """شمارش فقط حروف (فارسی، انگلیسی و عربی) - بدون فاصله، عدد و علامت"""
    return sum(1 for c in text if c.isalpha())


@login_required
def story_create(request):
    """ساخت داستان جدید"""
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            
            first_text = request.POST.get('first_segment', '').strip()
            letters = count_letters(first_text)
            
            if letters < 50:
                messages.error(
                    request, 
                    f'بخش اول داستان باید حداقل ۵۰ حرف داشته باشه. الان فقط {letters} حرف داری.'
                )
                return render(request, 'stories/story_create.html', {'form': form})
            
            with transaction.atomic():
                story.save()
                Segment.objects.create(
                    story=story,
                    author=request.user,
                    text=first_text,
                    is_canon=True,
                )
                story.total_segments = 1
                story.save(update_fields=['total_segments'])
                request.user.total_stories = F('total_stories') + 1
                request.user.save(update_fields=['total_stories'])
            
            messages.success(request, 'داستانت با موفقیت شروع شد! 🎉')
            return redirect(story.get_absolute_url())
    else:
        form = StoryForm()
    
    return render(request, 'stories/story_create.html', {'form': form})


@login_required
@require_POST
def add_segment(request, slug):
    """اضافه کردن ادامه به داستان"""
    story = get_object_or_404(Story, slug=slug)
    form = SegmentForm(request.POST)
    
    if form.is_valid():
        last_canon = story.segments.filter(is_canon=True).order_by('-created_at').first()
        
        segment = form.save(commit=False)
        segment.story = story
        segment.author = request.user
        segment.parent = last_canon
        
        with transaction.atomic():
            segment.save()
            Story.objects.filter(pk=story.pk).update(total_segments=F('total_segments') + 1)
            request.user.total_continuations = F('total_continuations') + 1
            request.user.save(update_fields=['total_continuations'])
            
            # ← نوتیفیکیشن به نویسنده داستان
            Notification.create_segment_notification(segment)
        
        messages.success(request, 'ادامه‌ات ثبت شد! ✍️')
    else:
        for error in form.errors.values():
            messages.error(request, error.as_text())
    
    return redirect(story.get_absolute_url())


@login_required
@require_POST
def vote_segment(request, segment_id):
    """رأی دادن یا برداشتن رأی"""
    segment = get_object_or_404(Segment, pk=segment_id)
    story = segment.story
    
    with transaction.atomic():
        vote, created = Vote.objects.get_or_create(user=request.user, segment=segment)
        
        if created:
            Segment.objects.filter(pk=segment.pk).update(votes=F('votes') + 1)
            Story.objects.filter(pk=story.pk).update(total_votes=F('total_votes') + 1)
            segment.author.total_votes_received = F('total_votes_received') + 1
            segment.author.save(update_fields=['total_votes_received'])
            
            # ← نوتیفیکیشن به نویسنده ادامه
            Notification.create_vote_notification(segment, request.user)
            
            messages.success(request, 'رأیت ثبت شد! ❤️')
        else:
            vote.delete()
            Segment.objects.filter(pk=segment.pk).update(votes=F('votes') - 1)
            Story.objects.filter(pk=story.pk).update(total_votes=F('total_votes') - 1)
            segment.author.total_votes_received = F('total_votes_received') - 1
            segment.author.save(update_fields=['total_votes_received'])
            messages.info(request, 'رأیت برداشته شد.')
    
    return redirect(story.get_absolute_url() + f'#segment-{segment.id}')


@login_required
@require_POST
def select_canon(request, segment_id):
    """انتخاب ادامه رسمی (فقط نویسنده داستان)"""
    segment = get_object_or_404(Segment, pk=segment_id)
    story = segment.story
    
    if request.user != story.author:
        messages.error(request, 'فقط نویسنده داستان می‌تونه ادامه رسمی رو انتخاب کنه.')
        return redirect(story.get_absolute_url())
    
    with transaction.atomic():
        segment.is_canon = True
        segment.save(update_fields=['is_canon'])
        
        Segment.objects.filter(
            story=story, parent=segment.parent, is_canon=False
        ).exclude(pk=segment.pk).update(is_canon=False)
        
        # ← نوتیفیکیشن به نویسنده ادامه
        Notification.create_canon_notification(segment)
        
        messages.success(request, 'این ادامه به عنوان ادامه رسمی انتخاب شد! ⭐')
    
    return redirect(story.get_absolute_url())


def search_view(request):
    """جستجو توی داستان‌ها، نویسندگان و ادامه‌ها"""
    query = request.GET.get('q', '').strip()
    
    stories = Story.objects.none()
    authors = []
    segments = Segment.objects.none()
    
    if query and len(query) >= 2:
        stories = Story.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status='active'
        ).select_related('author', 'genre').order_by('-total_votes')[:20]
        
        from accounts.models import User
        authors = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).order_by('-total_stories')[:10]
        
        segments = Segment.objects.filter(
            text__icontains=query
        ).select_related('story', 'author').order_by('-votes')[:10]
    
    return render(request, 'stories/search.html', {
        'query': query,
        'stories': stories,
        'authors': authors,
        'segments': segments,
        'has_results': stories.exists() or authors or segments.exists(),
    })
