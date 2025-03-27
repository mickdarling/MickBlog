"""
Custom admin site configuration for MickBlog.

This module contains a direct registration of the SiteConfig model to ensure it
appears in the admin interface even if there's an issue with the decorator-based registration.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from .models import SiteConfig
from .admin.views import ai_editor_view, ai_config_view, apply_changes_view, test_json_view
import reversion
from reversion.admin import VersionAdmin
import traceback
import time
import os
from django.contrib import messages
from django.conf import settings

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
        """Add custom URLs for the AI editor interface and version history"""
        urls = super().get_urls()
        custom_urls = [
            path('ai_editor/', self.admin_site.admin_view(ai_editor_view), name='ai-config-editor'),
            path('ai_config/', self.admin_site.admin_view(ai_config_view), name='ai-config-generate'),
            path('apply_changes/', self.admin_site.admin_view(apply_changes_view), name='ai-config-apply'),
            path('test_json/', test_json_view, name='test-json'),
            path('config-history/', self.admin_site.admin_view(self.config_history_view), name='config-history'),
            # Add revision history URLs
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='core_siteconfig_history'),
            path('<path:object_id>/history/<int:version_id>/', self.admin_site.admin_view(self.revision_view), name='core_siteconfig_revision'),
            path('recover/<int:version_id>/', self.admin_site.admin_view(self.recover_view), name='core_siteconfig_recover'),
        ]
        return custom_urls + urls
        
    def history_view(self, request, object_id):
        """Custom history view that overrides the default django-reversion history view"""
        config = SiteConfig.get()
        history = reversion.models.Version.objects.get_for_object(config)
        
        context = {
            'history': history,
            'config': config,
            'title': 'Configuration History',
        }
        
        return render(request, 'admin/core/siteconfig/history.html', context)
        
    def revision_view(self, request, object_id, version_id):
        """View to show a specific revision"""
        from reversion.models import Version
        
        config = SiteConfig.get()
        version = Version.objects.get(pk=version_id)
        
        # Get the old data
        version_data = version.field_dict
        
        # Get the current data
        current_data = {}
        for field_name, value in version_data.items():
            if hasattr(config, field_name):
                current_data[field_name] = getattr(config, field_name)
        
        # Compare the two versions to find changes
        changes = {}
        for field, old_value in version_data.items():
            if field in current_data:
                new_value = current_data[field]
                # Only include fields that have changed
                if old_value != new_value:
                    # For large text fields, show a preview
                    if isinstance(old_value, str) and len(old_value) > 200:
                        old_value = f"{old_value[:200]}..."
                    if isinstance(new_value, str) and len(new_value) > 200:
                        new_value = f"{new_value[:200]}..."
                    changes[field] = (new_value, old_value)  # Note: current first, version second
        
        context = {
            'title': f'Version {version_id} of {config}',
            'config': config,
            'version': version,
            'data': version_data,
            'current_data': current_data,
            'changes': changes,
            'can_revert': True,
        }
        
        return render(request, 'admin/core/siteconfig/history_comparison.html', context)
        
    def recover_view(self, request, version_id):
        """View to recover a specific version"""
        from reversion.models import Version
        import reversion
        
        if not self.has_change_permission(request):
            raise PermissionDenied
            
        version = Version.objects.get(pk=version_id)
        
        if request.method == 'POST':
            # Actually restore the content
            with reversion.create_revision():
                # Get the current SiteConfig instance
                config = SiteConfig.get()
                
                # Get the serialized data from the version
                version_data = version.field_dict
                
                # Update all fields from the version data
                for field_name, value in version_data.items():
                    if hasattr(config, field_name):
                        setattr(config, field_name, value)
                
                # Save the config to apply changes
                config.save()
                
                # Set revision metadata
                reversion.set_user(request.user)
                reversion.set_comment(f"Reverted to version from {version.revision.date_created}")
                
                # Add success message
                messages.success(request, f"Successfully reverted to version from {version.revision.date_created}")
                
                # Redirect to the config change form
                return redirect('admin:core_siteconfig_change', 1)
        else:
            # Display confirmation page
            context = {
                'title': f'Recover {version_id}',
                'version': version,
                'config': SiteConfig.get(),
                'data': version.field_dict,
                'opts': self.model._meta,
            }
            
            return render(request, 'admin/core/siteconfig/recover_confirmation.html', context)
    
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

# Direct registration to ensure model is in admin
admin.site.register(SiteConfig, SiteConfigAdmin)