from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """لیست همه نوتیفیکیشن‌ها"""
    notifications = request.user.notifications.select_related('sender', 'story', 'segment')
    
    unread_only = request.GET.get('unread') == '1'
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return render(request, 'notifications/list.html', {
        'notifications': notifications[:100],
        'unread_count': request.user.notifications.filter(is_read=False).count(),
        'unread_only': unread_only,
    })


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """علامت‌گذاری یه نوتیفیکیشن به عنوان خوانده‌شده"""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect(notification.url or 'notifications:list')


@login_required
def unread_count(request):
    """تعداد نوتیفیکیشن‌های خوانده‌نشده (برای آیکون هدر)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


@login_required
@require_POST
def mark_all_read(request):
    """علامت‌گذاری همه به عنوان خوانده‌شده"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')