import os
from django.db import models
from django.conf import settings
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import reversion


@reversion.register()
class SiteConfig(models.Model):
    """
    Singleton model for site-wide configuration.
    
    This model implements a singleton pattern to ensure only one site configuration exists.
    It stores all configuration in the database and supports version history through django-reversion.
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
    
    # Custom CSS content
    custom_css = models.TextField(blank=True, help_text="Custom CSS to be applied to the entire site")
    
    # Updated timestamp
    updated_at = models.DateTimeField(auto_now=True, help_text="When this configuration was last updated")
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return "Site Configuration"
    
    def save(self, *args, **kwargs):
        # Enforce singleton pattern by always using PK=1
        # This ensures there's only ever one SiteConfig instance
        self.pk = 1
        
        # Save to database
        super().save(*args, **kwargs)
    
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
    
    def get_custom_css_path(self):
        """
        Returns the path to the custom CSS file.
        """
        return os.path.join(settings.STATIC_ROOT, 'css', 'custom.css')
        
    def save_custom_css(self):
        """
        Save the custom CSS to a file in the static directory.
        This allows it to be served efficiently by the web server.
        """
        if self.custom_css:
            css_dir = os.path.join(settings.STATIC_ROOT, 'css')
            os.makedirs(css_dir, exist_ok=True)
            
            css_file = os.path.join(css_dir, 'custom.css')
            with open(css_file, 'w') as f:
                f.write(self.custom_css)
                
    def to_dict(self):
        """
        Returns a dictionary representation of the configuration.
        Useful for serialization and AI processing.
        """
        return {
            'site_info': {
                'title': self.title,
                'tagline': self.tagline,
                'brand': self.brand,
                'footer_text': self.footer_text,
                'meta_description': self.meta_description,
            },
            'colors': {
                'primary_color': self.primary_color,
                'secondary_color': self.secondary_color,
            },
            'content': {
                'about_text': self.about_text,
            },
            'contact': {
                'email': self.email,
                'phone': self.phone,
                'address': self.address,
            },
            'social': {
                'github_url': self.github_url,
                'linkedin_url': self.linkedin_url,
                'twitter_url': self.twitter_url,
                'facebook_url': self.facebook_url,
                'instagram_url': self.instagram_url,
                'bluesky_url': self.bluesky_url,
            },
            'analytics': {
                'google_analytics_id': self.google_analytics_id,
            },
            'appearance': {
                'custom_css': self.custom_css,
            },
            'system': {
                'maintenance_mode': self.maintenance_mode,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }
        }