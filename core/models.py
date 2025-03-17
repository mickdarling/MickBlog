import os
import subprocess
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from pathlib import Path


class SiteConfig(models.Model):
    """
    Singleton model for site-wide configuration.
    
    This model implements a singleton pattern to ensure only one site configuration exists.    
    It maintains a two-way sync between the database and site_config.md file using Django signals.
    """
    # Site information fields
    title = models.CharField(max_length=100, default="Mick Blog", help_text="Main site title used in browser tab and header")
    tagline = models.CharField(max_length=200, blank=True, help_text="Short description shown on homepage")
    brand = models.CharField(max_length=10, default="MB", help_text="Short text or acronym for navbar brand")
    
    # Color scheme customization
    primary_color = models.CharField(max_length=20, default="#007bff", help_text="Main color theme (hex code)")
    secondary_color = models.CharField(max_length=20, default="#6c757d", help_text="Secondary color theme (hex code)")
    
    # Site assets
    favicon = models.ImageField(upload_to='site/', blank=True, help_text="Site favicon")
    logo = models.ImageField(upload_to='site/', blank=True, help_text="Site logo")
    
    # Content fields
    about_text = MarkdownxField(blank=True, help_text="Content for About page in Markdown format")
    footer_text = models.CharField(max_length=500, blank=True, help_text="Text displayed in page footer")
    
    # Social media links - all optional
    github_url = models.URLField(blank=True, help_text="GitHub profile URL")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")
    facebook_url = models.URLField(blank=True, help_text="Facebook profile URL")
    instagram_url = models.URLField(blank=True, help_text="Instagram profile URL")
    bluesky_url = models.URLField(blank=True, help_text="Bluesky profile URL")
    
    # Contact information - all optional
    email = models.EmailField(blank=True, help_text="Public contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Public contact phone number")
    address = models.TextField(blank=True, help_text="Physical address")
    
    # SEO and monitoring
    google_analytics_id = models.CharField(max_length=50, blank=True, help_text="Google Analytics tracking ID")
    maintenance_mode = models.BooleanField(default=False, help_text="Enable maintenance mode for the site")
    meta_description = models.TextField(blank=True, help_text="SEO description for the site") 
    
    # Public class variable to control signal triggering
    # This avoids attribute errors when checking for _skip_signal
    skip_signal = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instance level flag to prevent infinite loops in signals
        self._skip_signal = False
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return "Site Configuration"
    
    def save(self, *args, **kwargs):
        # Enforce singleton pattern by always using PK=1
        # This ensures there's only ever one SiteConfig instance
        self.pk = 1
        
        # Debug print to track save operations - would be better with proper logging
        print(f"MODEL SAVE: Saving SiteConfig with title={self.title}, skip_signal={getattr(self, '_skip_signal', False)}")
        
        # Save to database
        super().save(*args, **kwargs)
        
        # Debug print after save
        print(f"MODEL SAVE COMPLETE: SiteConfig saved with id={self.pk}")
    
    @classmethod
    def get(cls):
        """
        Get site configuration singleton, creating it if it doesn't exist.
        
        This method ensures we always have a valid configuration object to work with,
        avoiding the need for null checks throughout the codebase.
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config
    
    @property
    def formatted_about(self):
        """
        Returns the about_text field rendered from Markdown to HTML.
        This allows writing content in Markdown but displaying as HTML.
        """
        return markdownify(self.about_text)


# Thread-safe synchronization mechanism
# This flag prevents multiple concurrent exports which could corrupt the file
_export_in_progress = False

@receiver(post_save, sender=SiteConfig)
def export_config_to_file(sender, instance, created, **kwargs):
    """
    Export site configuration to markdown file when the model is saved.
    
    This signal handler implements a one-way sync from database to file,
    ensuring the site_config.md file always reflects the current database state.
    The complementary update_site_config management command handles file-to-database sync.
    
    Thread safety is implemented using the _export_in_progress flag and _skip_signal attribute
    to prevent infinite loops that could occur with bidirectional sync.
    """
    global _export_in_progress
    
    # Log that signal was received
    print(f"POST_SAVE SIGNAL: Received for SiteConfig id={instance.pk}, title={instance.title}")
    
    # Skip if signaled to do so (to prevent infinite loops) or if an export is already in progress
    if getattr(instance, '_skip_signal', False) or _export_in_progress:
        print(f"POST_SAVE SIGNAL: Skipping export. skip_signal={getattr(instance, '_skip_signal', False)}, export_in_progress={_export_in_progress}")
        return
    
    print(f"POST_SAVE SIGNAL: Exporting config to file for title={instance.title}")
    
    # Set flag to prevent reentry - ensures only one export happens at a time
    _export_in_progress = True
    
    try:
        # Run the export_site_config command directly to update the file
        # This approach allows reusing all the file formatting logic in the command
        from django.core import management
        management.call_command('export_site_config', verbosity=1)
        print("POST_SAVE SIGNAL: Site configuration exported to file successfully")
    except Exception as e:
        import traceback
        print(f"POST_SAVE SIGNAL: Error exporting site configuration: {e}")
        traceback.print_exc()
    finally:
        # Always clear the flag when done to prevent deadlocks
        _export_in_progress = False