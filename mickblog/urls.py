"""
URL configuration for mickblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import api_key_form, set_api_key

# Admin site customization
admin.site.site_header = "MickBlog Admin"
admin.site.site_title = "MickBlog Admin Portal"
admin.site.index_title = "Welcome to MickBlog Admin Portal"

# Add direct admin URLs
admin_patterns = [
    path('admin/api-key-setup/', api_key_form, name='api-key-setup'),
    path('admin/set-api-key/', set_api_key, name='set-api-key'),
]

urlpatterns = admin_patterns + [
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('', include('core.urls', namespace='core')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('resume/', include('resume.urls', namespace='resume')),
    path('contact/', include('contact.urls', namespace='contact')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
