import os
import re
import yaml
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import SiteConfig

class Command(BaseCommand):
    """
    Management command for updating site configuration from site_config.md file.
    
    This command is a critical component of the site customization system,
    implementing the file-to-database sync direction. It parses the markdown file's
    YAML and code blocks, then updates the SiteConfig model accordingly.
    
    Usage:
        python manage.py update_site_config
    """
    help = 'Updates site configuration from the site_config.md file'
    
    def handle(self, *args, **options):
        """
        Main command execution method.
        
        Reads the site_config.md file, parses its sections, and updates the
        SiteConfig model with extracted values. Also generates a custom CSS file
        from the CSS section.
        """
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
        
        # IMPORTANT: Set flag to prevent post_save signal from triggering export
        # This breaks the potential infinite loop between file and database updates
        config._skip_signal = True
        print(f"UPDATE_SITE_CONFIG: Setting _skip_signal=True before saving")
        
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
            # Handle Bluesky separately since it might be a newer addition
            config.bluesky_url = social.get('bluesky_url', config.bluesky_url)
        
        if analytics:
            config.google_analytics_id = analytics.get('google_analytics_id', config.google_analytics_id)
        
        # Save config to database
        config.save()
        
        # Create custom CSS file in static directory
        if custom_css:
            css_dir = os.path.join(settings.BASE_DIR, 'static', 'css')
            os.makedirs(css_dir, exist_ok=True)
            css_file = os.path.join(css_dir, 'custom.css')
            
            with open(css_file, 'w') as f:
                f.write(custom_css)
            
            self.stdout.write(self.style.SUCCESS(f'Custom CSS written to {css_file}'))
        
        self.stdout.write(self.style.SUCCESS('Site configuration updated successfully'))
    
    def _parse_yaml_block(self, content, section_name):
        """
        Parse YAML block from markdown file for a specific section.
        
        This method extracts and parses YAML content between triple backtick fences
        following a section header. It handles error reporting for invalid YAML.
        
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
        pattern = rf'## {section_name}\s*```markdown\s*(.*?)\s*```'
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