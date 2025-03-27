"""
Utility functions for the core app.
"""
import os
import re
import environ
from django.conf import settings

def reload_env_settings():
    """
    Reload environment variables from .env file.
    
    This function is useful after updating the .env file to 
    make the new values available without restarting the server.
    """
    # Initialize environ
    env = environ.Env()
    
    # Get the path to the .env file
    dotenv_path = os.path.join(settings.BASE_DIR, '.env')
    
    # Skip if .env file doesn't exist
    if not os.path.exists(dotenv_path):
        return False
    
    # Force reload of .env file
    environ.Env.read_env(dotenv_path, overwrite=True)
    
    # Update settings with the new values from environment
    if 'ANTHROPIC_API_KEY' in os.environ:
        settings.ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
        return True
        
    # If environment variable isn't set, try to read directly from .env file
    # This is a fallback for Docker environments where env vars might not be properly updated
    try:
        with open(dotenv_path, 'r') as f:
            content = f.read()
            
        # Look for API key in the .env file
        match = re.search(r'ANTHROPIC_API_KEY=([^\n]+)', content)
        if match:
            # Get the raw API key and clean it up
            api_key = match.group(1).strip().strip('"\'')
            settings.ANTHROPIC_API_KEY = api_key
            print(f"API key loaded directly from .env file: {api_key[:5]}... (length: {len(api_key)})")
            return True
    except Exception as e:
        print(f"Error reading .env file directly: {str(e)}")
        
    return False

def get_anthropic_api_key():
    """
    Get the Anthropic API key, with multiple fallbacks.
    
    This ensures we have the most up-to-date API key from various sources.
    """
    # First check if it's already in settings
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    
    # If not in settings, try environment
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        
    # If still not found, try to reload from .env file
    if not api_key:
        reload_env_settings()
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    
    # Finally, try to read directly from .env file as last resort
    if not api_key:
        dotenv_path = os.path.join(settings.BASE_DIR, '.env')
        try:
            with open(dotenv_path, 'r') as f:
                content = f.read()
                
            match = re.search(r'ANTHROPIC_API_KEY=([^\n]+)', content)
            if match:
                api_key = match.group(1).strip().strip('"\'')
                print(f"API key read from .env directly: {api_key[:5]}... (length: {len(api_key)})")
        except Exception:
            pass
            
    return api_key