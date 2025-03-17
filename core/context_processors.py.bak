from django.conf import settings
import datetime
import random

def site_settings(request):
    """
    Add site settings to template context, using data from the SiteConfigMiddleware
    """
    # Get the timestamp for cache busting
    timestamp = datetime.datetime.now().timestamp()
    random_val = random.randint(1, 1000000)  # Add randomness for extra cache busting
    
    # Get site_config attached by middleware
    if hasattr(request, 'site_config') and request.site_config:
        site_config = request.site_config
        
        # Use database values, fallback to settings.py
        context = {
            'SITE_TITLE': site_config.title or settings.SITE_TITLE,
            'SITE_BRAND': site_config.brand or settings.SITE_BRAND,
            'PRIMARY_COLOR': site_config.primary_color or settings.PRIMARY_COLOR,
            'SECONDARY_COLOR': site_config.secondary_color or settings.SECONDARY_COLOR,
            'site': site_config,  # Add the entire site config object for easy access
            'cache_buster': f"{timestamp}-{random_val}",  # Add timestamp to prevent caching
        }
        
        print(f"Context processor using middleware title: {context['SITE_TITLE']}")
        return context
    else:
        # If middleware didn't attach site_config, fallback to settings
        print("Context processor falling back to settings (no middleware data)")
        return {
            'SITE_TITLE': settings.SITE_TITLE,
            'SITE_BRAND': settings.SITE_BRAND,
            'PRIMARY_COLOR': settings.PRIMARY_COLOR,
            'SECONDARY_COLOR': settings.SECONDARY_COLOR,
            'cache_buster': f"{timestamp}-{random_val}",
        }