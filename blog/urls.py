from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('category/<slug:slug>/', views.post_list, name='category'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # AI Post Generator (Form-based)
    path('ai_post_generator/', views.ai_post_generator_view, name='ai_post_generator'),
    path('generate_ai_post/', views.generate_ai_post_view, name='generate_ai_post'),
    
    # AI Blog Editor (Conversational)
    path('ai_blog_editor/', views.ai_blog_editor_view, name='ai_blog_editor'),
    path('ai_blog_conversation/', views.ai_blog_conversation_view, name='ai_blog_conversation'),
    path('ai_blog_improve/', views.ai_blog_improve_view, name='ai_blog_improve'),
    path('markdown_preview/', views.markdown_preview_view, name='markdown_preview'),
    path('save_ai_blog/', views.save_ai_blog_view, name='save_ai_blog'),
]