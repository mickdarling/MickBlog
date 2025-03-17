from django.shortcuts import render
from django.http import HttpResponse
from .models import Education, Experience, Skill, Certification
from core.models import SiteConfig
from django.template.loader import render_to_string
from django.conf import settings
import os

def resume(request):
    """View for the resume page"""
    # Get site configuration
    site = SiteConfig.get()
    
    # Get all resume components
    education = Education.objects.all()
    experiences = Experience.objects.all()
    skills = Skill.objects.all()
    certifications = Certification.objects.all()
    
    context = {
        'site': site,
        'education': education,
        'experiences': experiences,
        'skills': skills,
        'certifications': certifications,
    }
    
    return render(request, 'resume/resume.html', context)

def download_resume(request):
    """
    View for downloading the resume as PDF
    This is a placeholder - in a real implementation, 
    you would use a library like WeasyPrint to convert HTML to PDF
    """
    # For demonstration purposes, we'll just return a text response
    # In a production app, you would generate a PDF and return it
    
    response = HttpResponse(
        "This would be a PDF download of the resume in a real implementation.",
        content_type="text/plain"
    )
    response['Content-Disposition'] = 'attachment; filename="resume.txt"'
    
    return response