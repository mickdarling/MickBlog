"""
Custom admin site configuration for MickBlog.

This module contains a direct registration of the SiteConfig model to ensure it
appears in the admin interface even if there's an issue with the decorator-based registration.
"""

from django.contrib import admin
from django.urls import path
from .models import SiteConfig
from .admin.views import ai_editor_view, ai_message_view, apply_changes_view
import traceback
import time
from django.contrib import messages
from django.core.management import call_command

class SiteConfigAdmin(admin.ModelAdmin):
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
        ('AI Configuration', {
            'fields': ('anthropic_api_key',),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        """Add custom URLs for the AI editor interface"""
        urls = super().get_urls()
        custom_urls = [
            path('ai_editor/', self.admin_site.admin_view(ai_editor_view), name='ai-config-editor'),
            path('ai_message/', self.admin_site.admin_view(ai_message_view), name='ai-config-message'),
            path('apply_changes/', self.admin_site.admin_view(apply_changes_view), name='ai-config-apply'),
        ]
        return custom_urls + urls
    
    def has_add_permission(self, request):
        # Limit to only one instance
        return not SiteConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
    
    def save_model(self, request, obj, form, change):
        """Override save_model to ensure changes are correctly saved and exported"""
        # Debug: Print what's being saved
        print(f"ADMIN SAVE: Saving site config with title={obj.title}")
        
        try:
            # First save to database normally
            super().save_model(request, obj, form, change)
            
            # Manually run the export command
            print("ADMIN SAVE: Running export_site_config command")
            call_command('export_site_config', verbosity=1)
            
            # Show success message
            messages.success(request, "Site configuration updated successfully. Changes are live on the site.")
            
        except Exception as e:
            # Log any errors
            print(f"ERROR in admin save_model: {e}")
            traceback.print_exc()
            # Show error message
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
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

# Direct registration to ensure model is in admin
admin.site.register(SiteConfig, SiteConfigAdmin)