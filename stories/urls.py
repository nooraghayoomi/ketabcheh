from django.urls import path, re_path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.story_list, name='list'),
    path('search/', views.search_view, name='search'),
    path('create/', views.story_create, name='create'),
    re_path(r'^(?P<slug>[-\w]+)/$', views.story_detail, name='detail'),
    re_path(r'^(?P<slug>[-\w]+)/add/$', views.add_segment, name='add_segment'),
    path('segment/<int:segment_id>/vote/', views.vote_segment, name='vote'),
    path('segment/<int:segment_id>/canon/', views.select_canon, name='select_canon'),
]