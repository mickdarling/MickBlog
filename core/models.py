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
    
    # AI configuration
    anthropic_api_key = models.CharField(max_length=255, blank=True, help_text="Anthropic API key for AI-powered site configuration editor - usually 83 characters or longer")
    
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
    
    def export_to_markdown(self):
        """
        Export the current configuration to markdown format.
        
        This formats all configuration fields into a structured markdown document
        with appropriate YAML and code blocks, matching the format expected by
        the update_site_config management command.
        
        Returns:
            str: The markdown representation of the site configuration
        """
        # Build the markdown content section by section
        markdown = "# Site Configuration Template\n\n"
        markdown += "This markdown file allows you to easily customize the content, style, and configuration of your MickBlog site. Edit the sections below and migrate the database to apply changes.\n\n"
        
        # Site Information section
        markdown += "## Site Information\n\n"
        markdown += "```yaml\n"
        markdown += f"brand: {self.brand}\n"
        markdown += f"footer_text: \"{self.footer_text}\"\n"
        markdown += f"meta_description: {self.meta_description}\n"
        markdown += f"tagline: {self.tagline}\n"
        markdown += f"title: {self.title}\n\n"
        markdown += "```\n\n"
        
        # Colors and Styling
        markdown += "## Colors and Styling\n\n"
        markdown += "```yaml\n"
        markdown += f"primary_color: '{self.primary_color}'\n"
        markdown += f"secondary_color: '{self.secondary_color}'\n\n"
        markdown += "```\n\n"
        
        # Custom CSS - placeholder section
        markdown += "## Custom CSS\n\n"
        markdown += "Add any custom CSS below. This will be applied to the entire site.\n\n"
        
        # Read the custom CSS file if it exists
        custom_css = ""
        css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'custom.css')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                custom_css = f.read()
        
        markdown += "```css\n"
        markdown += custom_css if custom_css else "/* Custom CSS styles */\n"
        markdown += "```\n\n"
        
        # About Me section
        markdown += "## About Me\n\n"
        markdown += "Write your about information in markdown format below.\n\n"
        markdown += "```markdown\n"
        markdown += self.about_text if self.about_text else "I am a software developer with experience in web development."
        markdown += "\n```\n\n"
        
        # Contact Information
        markdown += "## Contact Information\n\n"
        markdown += "```yaml\n"
        markdown += f"address: '{self.address}'\n"
        markdown += f"email: {self.email}\n"
        markdown += f"phone: '{self.phone}'\n\n"
        markdown += "```\n\n"
        
        # Social Media
        markdown += "## Social Media\n\n"
        markdown += "```yaml\n"
        markdown += f"bluesky_url: {self.bluesky_url}\n"
        markdown += f"facebook_url: {self.facebook_url}\n"
        markdown += f"github_url: {self.github_url}\n"
        markdown += f"instagram_url: {self.instagram_url}\n"
        markdown += f"linkedin_url: {self.linkedin_url}\n\n"
        markdown += "```\n\n"
        
        # Google Analytics
        markdown += "## Google Analytics\n\n"
        markdown += "```yaml\n"
        markdown += f"google_analytics_id: {self.google_analytics_id}\n\n"
        markdown += "```\n\n"
        
        # AI Configuration
        markdown += "## AI Configuration\n\n"
        markdown += "```yaml\n"
        markdown += f"anthropic_api_key: {self.anthropic_api_key}\n\n"
        markdown += "```\n\n"
        
        # How to apply changes section
        markdown += "---\n\n"
        markdown += "## How to Apply Changes\n\n"
        markdown += "After updating this file, run the following management command to apply the changes to your site:\n\n"
        markdown += "```bash\n"
        markdown += "python manage.py update_site_config\n"
        markdown += "```\n\n"
        markdown += "This will parse the markdown file and update the database with the new configuration."
        
        return markdown


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