"""
Management command to migrate configuration from site_config.md file to the database.
This is a one-time migration helper for the transition to database-only configuration.
"""
import os
import re
import yaml
from django.core.management.base import BaseCommand
from django.conf import settings
import reversion
from core.models import SiteConfig


class Command(BaseCommand):
    help = 'Migrates configuration from site_config.md file to the database'

    def handle(self, *args, **options):
        # Get path to configuration file
        config_file = os.path.join(settings.BASE_DIR, 'site_config.md')
        
        # Check if file exists
        if not os.path.exists(config_file):
            self.stdout.write(self.style.ERROR(f'Config file not found: {config_file}'))
            return
        
        # Read file content
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Parse yaml blocks for different configuration sections
        site_info = self._parse_yaml_block(content, 'Site Information')
        colors = self._parse_yaml_block(content, 'Colors and Styling')
        contact = self._parse_yaml_block(content, 'Contact Information')
        social = self._parse_yaml_block(content, 'Social Media')
        analytics = self._parse_yaml_block(content, 'Google Analytics')
        
        # Parse about content as markdown
        about_text = self._parse_markdown_block(content, 'About Me')
        
        # Parse custom CSS
        custom_css = self._parse_code_block(content, 'Custom CSS', 'css')
        
        # Get or create site config singleton
        config = SiteConfig.get()
        
        # Use reversion to track this migration
        with reversion.create_revision():
            # Update fields from parsed data, keeping existing values as fallback
            if site_info:
                config.title = site_info.get('title', config.title)
                config.tagline = site_info.get('tagline', config.tagline)
                config.brand = site_info.get('brand', config.brand)
                config.footer_text = site_info.get('footer_text', config.footer_text)
                config.meta_description = site_info.get('meta_description', config.meta_description)
            
            if colors:
                config.primary_color = colors.get('primary_color', config.primary_color)
                config.secondary_color = colors.get('secondary_color', config.secondary_color)
            
            if about_text:
                config.about_text = about_text
            
            if contact:
                config.email = contact.get('email', config.email)
                config.phone = contact.get('phone', config.phone)
                config.address = contact.get('address', config.address)
            
            if social:
                config.github_url = social.get('github_url', config.github_url)
                config.linkedin_url = social.get('linkedin_url', config.linkedin_url)
                config.twitter_url = social.get('twitter_url', config.twitter_url)
                config.facebook_url = social.get('facebook_url', config.facebook_url)
                config.instagram_url = social.get('instagram_url', config.instagram_url)
                config.bluesky_url = social.get('bluesky_url', config.bluesky_url)
            
            if analytics:
                config.google_analytics_id = analytics.get('google_analytics_id', config.google_analytics_id)
                
            if custom_css:
                config.custom_css = custom_css
            
            # Save config to database
            config.save()
            
            # Set revision metadata
            reversion.set_comment("Migrated from site_config.md file")
            
            # Save custom CSS to file if provided
            if custom_css:
                config.save_custom_css()
        
        # Rename the old config file to avoid confusion
        backup_file = os.path.join(settings.BASE_DIR, 'site_config.md.bak')
        os.rename(config_file, backup_file)
        
        self.stdout.write(self.style.SUCCESS(f'Site configuration migrated successfully from file to database'))
        self.stdout.write(self.style.SUCCESS(f'Original file backed up to {backup_file}'))
    
    def _parse_yaml_block(self, content, section_name):
        """
        Parse YAML block from markdown file for a specific section.
        
        Args:
            content (str): Full markdown file content
            section_name (str): Section header to look for (without ## prefix)
            
        Returns:
            dict: Parsed YAML content as dictionary, or None if section not found or parsing failed
        """
        pattern = rf'## {section_name}\s*```yaml\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f'Error parsing YAML in section {section_name}: {e}'))
        
        return None
    
    def _parse_markdown_block(self, content, section_name):
        """
        Parse markdown content block for a specific section.
        
        Args:
            content (str): Full markdown file content
            section_name (str): Section header to look for (without ## prefix)
            
        Returns:
            str: Extracted markdown content, or None if section not found
        """
        pattern = rf'## {section_name}[^\#]*?```(?:markdown)?\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1)
        
        return None
    
    def _parse_code_block(self, content, section_name, language):
        """
        Parse code block for a specific language from a section.
        
        Args:
            content (str): Full markdown file content
            section_name (str): Section header to look for (without ## prefix)
            language (str): Language identifier in the code fence (e.g., 'css', 'js')
            
        Returns:
            str: Extracted code content, or None if section not found
        """
        pattern = rf'## {section_name}\s*```{language}\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1)
        
        return None