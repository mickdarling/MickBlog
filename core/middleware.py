from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
from core.models import SiteConfig

class SiteConfigMiddleware(MiddlewareMixin):
    """
    Middleware to inject site configuration into request for every view.
    
    This middleware attaches the SiteConfig singleton to every request object,
    making it available to all views without having to fetch it repeatedly.
    It supports the dynamic site customization system by providing the latest
    configuration data to templates.
    
    In case of errors (e.g., during initial setup before migrations), it provides
    a graceful fallback by setting site_config to None.
    """
    def process_request(self, request):
        # Attach site config directly to the request object using the singleton getter
        try:
            # Use get() instead of objects.get(pk=1) to handle first-run scenarios
            # where the SiteConfig object might not exist yet
            request.site_config = SiteConfig.get()
            print(f"SiteConfigMiddleware: Loaded title = {request.site_config.title}")
        except Exception as e:
            # Log error and set empty config for graceful degradation
            print(f"SiteConfigMiddleware error: {e}")
            request.site_config = None
        return None

class DisableBrowserCachingMiddleware(MiddlewareMixin):
    """
    Middleware to disable browser caching during development.
    
    This middleware ensures that developers always see the latest version of pages
    by adding cache control headers and injecting a timestamp into the HTML output.
    This is particularly important for the site customization system where changes
    should be immediately visible.
    
    In production, you may want to modify this to allow caching of static resources
    while still preventing caching of dynamic content.
    """
    def process_response(self, request, response):
        # Set headers to prevent all browser caching
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # For HTML responses, inject a timestamp comment before closing body tag
        # This ensures that even if browsers ignore cache headers, content will still differ
        current_time = int(time.time())
        if 'Content-Type' in response and 'text/html' in response['Content-Type']:
            try:
                content = response.content.decode('utf-8')
                if '</body>' in content:
                    # Add timestamp as HTML comment to force browser to recognize content as changed
                    timestamp_comment = f'<!-- Cache bust: {current_time} -->'
                    content = content.replace('</body>', f'{timestamp_comment}</body>')
                    response.content = content.encode('utf-8')
            except Exception as e:
                # If content modification fails, log error but still return response
                print(f"DisableBrowserCachingMiddleware error: {e}")
                
        return response