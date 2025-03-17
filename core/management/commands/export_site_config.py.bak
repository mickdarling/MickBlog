import os
import yaml
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import SiteConfig

class Command(BaseCommand):
    help = 'Exports site configuration from the database to the site_config.md file'
    
    def handle(self, *args, **options):
        config_file = os.path.join(settings.BASE_DIR, 'site_config.md')
        
        # Get site configuration
        config = SiteConfig.get()
        
        # Create fresh content from scratch
        site_info = {
            'title': config.title,
            'tagline': config.tagline,
            'brand': config.brand,
            'footer_text': config.footer_text,
            'meta_description': config.meta_description,
        }
        
        colors = {
            'primary_color': config.primary_color,
            'secondary_color': config.secondary_color,
        }
        
        contact = {
            'email': config.email,
            'phone': config.phone,
            'address': config.address,
        }
        
        social = {
            'github_url': config.github_url,
            'linkedin_url': config.linkedin_url,
            'bluesky_url': config.bluesky_url,
            'facebook_url': config.facebook_url,
            'instagram_url': config.instagram_url,
        }
        
        analytics = {
            'google_analytics_id': config.google_analytics_id,
        }
        
        # Get the CSS block from existing file if it exists
        custom_css = ""
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                css_match = re.search(r'## Custom CSS\s*```css\s*(.*?)\s*```', content, re.DOTALL)
                if css_match:
                    custom_css = css_match.group(1)
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'Creating new config file: {config_file}'))
        
        # Build a new config file from scratch
        new_content = """# Site Configuration Template

This markdown file allows you to easily customize the content, style, and configuration of your MickBlog site. Edit the sections below and migrate the database to apply changes.

## Site Information

```yaml
{site_info}
```

## Colors and Styling

```yaml
{colors}
```

## Custom CSS

Add any custom CSS below. This will be applied to the entire site.

```css
{custom_css}
```

## About Me

Write your about information in markdown format below.

```markdown
{about}
```

## Contact Information

```yaml
{contact}
```

## Social Media

```yaml
{social}
```

## Google Analytics

```yaml
{analytics}
```

---

## How to Apply Changes

After updating this file, run the following management command to apply the changes to your site:

```bash
python manage.py update_site_config
```

This will parse the markdown file and update the database with the new configuration."""
        
        # Format the template with our values
        new_content = new_content.format(
            site_info=yaml.dump(site_info, default_flow_style=False),
            colors=yaml.dump(colors, default_flow_style=False),
            custom_css=custom_css,
            about=config.about_text,
            contact=yaml.dump(contact, default_flow_style=False),
            social=yaml.dump(social, default_flow_style=False),
            analytics=yaml.dump(analytics, default_flow_style=False)
        )
        
        # Write to file
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        self.stdout.write(self.style.SUCCESS(f'Site configuration exported to {config_file}'))