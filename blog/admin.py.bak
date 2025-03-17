from django.contrib import admin
from .models import Category, Post
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author', 'category')
    search_fields = ('title', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    ordering = ('status', '-publish')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Content', {
            'fields': ('content', 'summary')
        }),
        ('Publication', {
            'fields': ('publish',),
            'classes': ('collapse',)
        }),
    )