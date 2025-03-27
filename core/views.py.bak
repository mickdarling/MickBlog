from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.conf import settings
import os
from blog.models import Post
from projects.models import Project
from .models import SiteConfig
from .utils import get_anthropic_api_key

def home(request):
    """Home page view"""
    # Get site configuration
    site = SiteConfig.get()
    
    # Get latest blog posts
    latest_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    
    # Get featured projects
    featured_projects = Project.objects.filter(featured=True).order_by('-start_date')[:3]
    
    context = {
        'site': site,
        'latest_posts': latest_posts,
        'featured_projects': featured_projects,
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """About page view"""
    # Get site configuration
    site = SiteConfig.get()
    
    context = {
        'site': site,
    }
    
    return render(request, 'core/about.html', context)
    
@staff_member_required
@require_POST
def set_api_key(request):
    """Save API key to .env file and update runtime settings"""
    api_key = request.POST.get('api_key')
    
    if api_key:
        # Strip any whitespace or quotes that might have been included
        clean_api_key = api_key.strip().strip('"\'')
        
        # Get the path to the .env file
        dotenv_path = os.path.join(settings.BASE_DIR, '.env')
        
        # Read existing content
        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add the API key
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith('ANTHROPIC_API_KEY='):
                new_lines.append(f'ANTHROPIC_API_KEY={clean_api_key}\n')
                updated = True
            else:
                new_lines.append(line)
                
        if not updated:
            new_lines.append(f'ANTHROPIC_API_KEY={clean_api_key}\n')
            
        # Write updated content
        with open(dotenv_path, 'w') as f:
            f.writelines(new_lines)
            
        # Update runtime setting
        settings.ANTHROPIC_API_KEY = clean_api_key
        
        # Log information about the saved key
        print(f"API key saved: {clean_api_key[:5]}... (length: {len(clean_api_key)})")
        
        # Create masked preview of API key for display
        api_key_preview = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "[Hidden]"
        
        messages.success(
            request, 
            f"API key updated successfully. Key {api_key_preview} is now active and ready to use."
        )
    else:
        messages.error(request, "API key cannot be empty.")
        
    # Redirect back to the API key form
    return redirect('api-key-setup')
    
@staff_member_required
def api_key_form(request):
    """View to display a dedicated API key form"""
    # Check current API key status using our robust method
    api_key = get_anthropic_api_key()
    api_key_set = bool(api_key)
    api_key_preview = None
    
    # Create a masked preview of the API key
    if api_key and len(api_key) > 10:
        api_key_preview = f"{api_key[:5]}...{api_key[-5:]}"
        print(f"API Key Form: API key available, starts with {api_key[:5]}")
        
    context = {
        'title': 'API Key Setup',
        'api_key_set': api_key_set,
        'api_key_preview': api_key_preview,
    }
    
    return render(request, 'admin/core/api_key_form.html', context)