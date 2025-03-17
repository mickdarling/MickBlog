from django.shortcuts import render
from blog.models import Post
from projects.models import Project
from .models import SiteConfig

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