from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Sum
from .forms import SignupForm, LoginForm, ProfileEditForm
from .models import User
from stories.models import Story, Segment, Vote


@require_http_methods(['GET', 'POST'])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'خوش آمدی {user.username}! 🎉')
            return redirect('home')
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کن.')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)
            messages.success(request, f'خوش برگشتی {user.username}! 👋')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'اطلاعات ورود نامعتبر است.')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f'{username} جان، با موفقیت خارج شدی. منتظرتیم! 👋')
    return redirect('home')


def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
        is_own_profile = request.user.is_authenticated and request.user == profile_user
    else:
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        profile_user = request.user
        is_own_profile = True
    user_stories = Story.objects.filter(author=profile_user).select_related('genre').order_by('-created_at')
    user_segments = Segment.objects.filter(author=profile_user).select_related('story').order_by('-created_at')[:10]
    stats = {
        'stories_count': user_stories.count(),
        'segments_count': Segment.objects.filter(author=profile_user).count(),
        'votes_received': Segment.objects.filter(author=profile_user).aggregate(total=Sum('votes'))['total'] or 0,
        'votes_given': Vote.objects.filter(user=profile_user).count(),
    }
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_stories': user_stories[:6],
        'user_segments': user_segments,
        'stats': stats,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایلت با موفقیت بروز شد. ✨')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'لطفاً خطاها رو برطرف کن.')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})