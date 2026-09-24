from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Report
from .forms import ReportForm
from stories.models import Story, Segment
from accounts.models import User


@login_required
@require_http_methods(['GET', 'POST'])
def report_story(request, slug):
    """گزارش یه داستان"""
    story = get_object_or_404(Story, slug=slug)
    
    if story.author == request.user:
        messages.error(request, 'نمی‌تونی داستان خودت رو گزارش بدی.')
        return redirect(story.get_absolute_url())
    
    if Report.objects.filter(reporter=request.user, story=story, status='pending').exists():
        messages.info(request, 'قبلاً این داستان رو گزارش دادی.')
        return redirect(story.get_absolute_url())
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.create_story_report(
                story=story,
                reporter=request.user,
                reason=form.cleaned_data['reason'],
                description=form.cleaned_data['description'],
            )
            messages.success(request, 'گزارشت ثبت شد. ممنون که کمک می‌کنی! 🙏')
            return redirect(story.get_absolute_url())
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'content_type': 'داستان',
        'content_title': story.title,
        'cancel_url': story.get_absolute_url(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def report_segment(request, segment_id):
    """گزارش یه ادامه"""
    segment = get_object_or_404(Segment, pk=segment_id)
    
    if segment.author == request.user:
        messages.error(request, 'نمی‌تونی ادامه خودت رو گزارش بدی.')
        return redirect(segment.story.get_absolute_url())
    
    if Report.objects.filter(reporter=request.user, segment=segment, status='pending').exists():
        messages.info(request, 'قبلاً این ادامه رو گزارش دادی.')
        return redirect(segment.story.get_absolute_url())
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.create_segment_report(
                segment=segment,
                reporter=request.user,
                reason=form.cleaned_data['reason'],
                description=form.cleaned_data['description'],
            )
            messages.success(request, 'گزارشت ثبت شد. ممنون که کمک می‌کنی! 🙏')
            return redirect(segment.story.get_absolute_url())
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'content_type': 'ادامه',
        'content_title': segment.text[:60] + '...',
        'cancel_url': segment.story.get_absolute_url(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def report_user(request, username):
    """گزارش یه کاربر"""
    reported_user = get_object_or_404(User, username=username)
    
    if reported_user == request.user:
        messages.error(request, 'نمی‌تونی خودت رو گزارش بدی.')
        return redirect('home')
    
    if Report.objects.filter(reporter=request.user, reported_user=reported_user, status='pending').exists():
        messages.info(request, 'قبلاً این کاربر رو گزارش دادی.')
        return redirect('accounts:user_profile', username=username)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.create_user_report(
                reported_user=reported_user,
                reporter=request.user,
                reason=form.cleaned_data['reason'],
                description=form.cleaned_data['description'],
            )
            messages.success(request, 'گزارشت ثبت شد. ممنون که کمک می‌کنی! 🙏')
            return redirect('accounts:user_profile', username=username)
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'content_type': 'کاربر',
        'content_title': reported_user.username,
        'cancel_url': f'/accounts/u/{username}/',
    })