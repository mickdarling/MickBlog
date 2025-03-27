from django.urls import path
from . import views
from .admin.views import test_json_view, ai_config_view, apply_changes_view

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('test_json/', test_json_view, name='test-json'),
    path('ai_config/', ai_config_view, name='ai-config'),
    path('apply_changes/', apply_changes_view, name='apply-changes'),
    path('admin/set-api-key/', views.set_api_key, name='set-api-key'),
    path('admin/api-key-form/', views.api_key_form, name='api-key-form'),
]