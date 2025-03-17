from django.shortcuts import render, get_object_or_404
from .models import Project, Technology
from core.models import SiteConfig

def project_list(request):
    """View for listing all projects"""
    # Get site configuration
    site = SiteConfig.get()
    
    # Get all projects ordered by featured and start date
    projects = Project.objects.all()
    
    context = {
        'projects': projects,
        'site': site,
    }
    
    return render(request, 'projects/project_list.html', context)

def project_detail(request, slug):
    """View for a specific project"""
    # Get site configuration
    site = SiteConfig.get()
    
    # Get the specific project
    project = get_object_or_404(Project, slug=slug)
    
    context = {
        'project': project,
        'site': site,
    }
    
    return render(request, 'projects/project_detail.html', context)