from django.contrib import admin
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from .models import SiteConfig
from .admin.views import ai_editor_view, ai_message_view, ai_config_view, apply_changes_view, test_json_view
import reversion
from reversion.admin import VersionAdmin
import traceback
import time
import os
from django.conf import settings

@admin.register(SiteConfig)
class SiteConfigAdmin(VersionAdmin):
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'tagline', 'brand', 'primary_color', 'secondary_color')
        }),
        ('Branding', {
            'fields': ('favicon', 'logo')
        }),
        ('Content', {
            'fields': ('about_text', 'footer_text', 'meta_description')
        }),
        ('Appearance', {
            'fields': ('custom_css',)
        }),
        ('Social Media', {
            'fields': ('github_url', 'linkedin_url', 'bluesky_url', 'facebook_url', 'instagram_url')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Advanced Settings', {
            'fields': ('google_analytics_id', 'maintenance_mode'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('updated_at',)
    
    def get_urls(self):
        """Add custom URLs for the AI editor interface"""
        urls = super().get_urls()
        custom_urls = [
            path('ai_editor/', self.admin_site.admin_view(ai_editor_view), name='ai-config-editor'),
            path('ai_message/', self.admin_site.admin_view(ai_message_view), name='ai-config-message'),
            path('ai_config/', self.admin_site.admin_view(ai_config_view), name='ai-config-generate'),
            path('apply_changes/', self.admin_site.admin_view(apply_changes_view), name='ai-config-apply'),
            path('test_json/', test_json_view, name='test-json'),
            path('config-history/', self.admin_site.admin_view(self.config_history_view), name='config-history'),
        ]
        return custom_urls + urls
    
    def config_history_view(self, request):
        """View to display configuration history and allow comparing versions"""
        config = SiteConfig.get()
        history = reversion.models.Version.objects.get_for_object(config)
        
        context = {
            'history': history,
            'config': config,
            'title': 'Configuration History',
        }
        
        return render(request, 'admin/core/siteconfig/history.html', context)
    
    def has_add_permission(self, request):
        # Limit to only one instance
        return not SiteConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure changes are correctly saved and CSS is exported.
        Using django-reversion's create_revision to automatically track changes.
        """
        print(f"ADMIN SAVE: Saving site config with title={obj.title}")
        
        try:
            with reversion.create_revision():
                # Save the model first
                super().save_model(request, obj, form, change)
                
                # Set revision metadata
                reversion.set_user(request.user)
                reversion.set_comment(f"Updated site configuration")
                
                # Save custom CSS to file if provided
                if obj.custom_css:
                    obj.save_custom_css()
                
                # Show success message
                messages.success(request, "Site configuration updated successfully.")
                
        except Exception as e:
            # Log any errors
            print(f"ERROR in admin save_model: {e}")
            traceback.print_exc()
            messages.error(request, f"Error updating site configuration: {e}")
            
    def response_change(self, request, obj):
        """Override response after successful save to refresh the page"""
        response = super().response_change(request, obj)
        
        # Add cache-busting parameter to force page refresh
        if 'Location' in response:
            response['Location'] += f"?_={int(time.time())}"
        
        return response
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change view to add button for AI editor"""
        extra_context = extra_context or {}
        extra_context['show_ai_editor_button'] = True
        extra_context['show_history_button'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
        
    def changelist_view(self, request, extra_context=None):
        """Make sure we always have a SiteConfig instance"""
        # Create the singleton if it doesn't exist
        SiteConfig.get()
        return super().changelist_view(request, extra_context=extra_context)