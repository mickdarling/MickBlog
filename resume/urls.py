from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('', views.resume, name='resume'),
    path('download/', views.download_resume, name='download'),
]