from django.contrib import admin
from .models import Genre, Story, Segment, Vote


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'status', 'total_segments', 'total_votes', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'genre', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'author', 'votes', 'is_canon', 'created_at')
    list_filter = ('is_canon', 'created_at')
    search_fields = ('text', 'author__username', 'story__title')
    raw_id_fields = ('story', 'parent', 'author')
    readonly_fields = ('votes',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'segment', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'segment')