from django.urls import path
from . import views
from .admin.views import test_json_view, ai_config_view, ai_message_view, apply_changes_view

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('test_json/', test_json_view, name='test-json'),
    path('ai_config/', ai_config_view, name='ai-config'),
    path('ai_message/', ai_message_view, name='ai-message'),
    path('apply_changes/', apply_changes_view, name='apply-changes'),
]