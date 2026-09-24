from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('story/<slug:slug>/', views.report_story, name='report_story'),
    path('segment/<int:segment_id>/', views.report_segment, name='report_segment'),
    path('user/<str:username>/', views.report_user, name='report_user'),
]