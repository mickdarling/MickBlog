from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from .models import Category, Post
from markdownx.admin import MarkdownxModelAdmin
from . import views

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
    
    def get_urls(self):
        """
        Add custom URLs for AI blog content generation tools
        
        Two complementary AI-powered blog creation tools are available:
        1. AI-AutoCreate - Form-based generator with structured parameters
           - Good for quick generation with specific attributes
           - Uses a form workflow with predefined fields
        
        2. AI Blog Editor - Conversational interface with real-time editing
           - Better for interactive content development 
           - Supports natural language requests and refinements
           - Includes diff view and improvement suggestions
        """
        urls = super().get_urls()
        custom_urls = [
            # AI-AutoCreate (form-based generator)
            path('ai_post_generator/', self.admin_site.admin_view(views.ai_post_generator_view), 
                 name='blog_ai_post_generator'),
                 
            # AI Blog Editor (conversational)
            path('ai_blog_editor/', self.admin_site.admin_view(views.ai_blog_editor_view), 
                 name='blog_ai_editor'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add buttons for AI tools to change list view"""
        extra_context = extra_context or {}
        extra_context['show_ai_generator_button'] = True
        extra_context['show_ai_editor_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

# Add AI buttons to admin index
class BlogAdminSite(admin.AdminSite):
    """Extend the admin site with custom actions"""
    
    def get_app_list(self, request):
        """
        Add AI tools to the blog application section.
        """
        app_list = super().get_app_list(request)
        
        # Find the blog app
        for app in app_list:
            if app['app_label'] == 'blog':
                # Add AI-AutoCreate link (form-based)
                app['models'].append({
                    'name': 'AI-AutoCreate',
                    'object_name': 'AIPostGenerator',
                    'admin_url': reverse('admin:blog_ai_post_generator'),
                    'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                })
                
                # Add AI Blog Editor link (conversational)
                app['models'].append({
                    'name': 'AI Blog Editor',
                    'object_name': 'AIBlogEditor',
                    'admin_url': reverse('admin:blog_ai_editor'),
                    'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                })
                break
                
        return app_list

# Register with the custom admin site
admin_site = BlogAdminSite(name='blog_admin')

# For Django admin template to show the AI tool buttons
admin.site.add_action(lambda modeladmin, request, queryset: redirect('admin:blog_ai_post_generator'), 
                     'AI-AutoCreate')
admin.site.add_action(lambda modeladmin, request, queryset: redirect('admin:blog_ai_editor'), 
                     'AI Blog Editor')