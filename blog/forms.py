from django import forms
from .models import Post, Category
from django.contrib.auth.models import User

class AIPostGeneratorForm(forms.Form):
    """Form for generating blog posts with AI assistance."""
    
    title = forms.CharField(
        max_length=250,
        required=False,
        help_text="Optional - leave empty for AI to generate a title",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    topic = forms.CharField(
        max_length=250, 
        required=True,
        help_text="Describe what you want to write about (required)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        help_text="Select a category for the post",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    length = forms.ChoiceField(
        choices=[
            ('short', 'Short (~300 words)'),
            ('medium', 'Medium (~600 words)'),
            ('long', 'Long (~1000 words)'),
        ],
        required=True,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tone = forms.ChoiceField(
        choices=[
            ('informative', 'Informative'),
            ('casual', 'Casual'),
            ('professional', 'Professional'),
            ('humorous', 'Humorous'),
            ('technical', 'Technical'),
        ],
        required=True,
        initial='informative',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    keywords = forms.CharField(
        max_length=200,
        required=False,
        help_text="Comma-separated keywords to include (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    publish_directly = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Create post as published (otherwise saved as draft)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )