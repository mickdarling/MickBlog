"""
Custom admin views for AI-powered site configuration editor.
"""
import os
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.management import call_command
from core.models import SiteConfig

@staff_member_required
def ai_editor_view(request):
    """Renders the AI editor interface"""
    config = SiteConfig.get()
    current_config = config.export_to_markdown()
    
    # Check if Anthropic API key is configured (either in env or model)
    api_key_configured = bool(settings.ANTHROPIC_API_KEY or config.anthropic_api_key)
    
    context = {
        'title': 'AI Site Configuration Editor',
        'config': config,
        'current_config': current_config,
        'api_key_configured': api_key_configured,
    }
    return render(request, 'admin/core/ai_editor.html', context)

@csrf_exempt
@staff_member_required
@require_http_methods(["POST"])
def ai_message_view(request):
    """Handles API interaction with Claude"""
    
    # Get API key from settings or model
    config = SiteConfig.get()
    api_key = settings.ANTHROPIC_API_KEY or config.anthropic_api_key
    
    if not api_key:
        return JsonResponse({'error': 'Anthropic API key not configured'}, status=500)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        message_history = data.get('history', [])
        
        config = SiteConfig.get()
        current_config = config.export_to_markdown()
        
        # Prepare the system message with current configuration
        system_message = f"""You are a Django site configuration assistant. 
You help edit the site_config.md file for a Django blog site.
The current site configuration is shown below:

```markdown
{current_config}
```

When editing, maintain the same structure and format. You can suggest specific changes
to any section. Be specific and helpful.
"""
        
        # Prepare messages for Claude API
        api_messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        for msg in message_history:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            
        # Add the current user message
        api_messages.append({"role": "user", "content": user_message})
        
        # Call Claude API
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "messages": api_messages
            },
            timeout=30
        )
        
        response_data = response.json()
        
        if response.status_code != 200:
            return JsonResponse({
                'error': f"API Error: {response_data.get('error', {}).get('message', 'Unknown error')}"
            }, status=500)
            
        ai_response = response_data['content'][0]['text']
        
        # Check if response contains a full markdown file
        has_suggested_config = False
        markdown_block = None
        
        if "```markdown" in ai_response and "```" in ai_response.split("```markdown", 1)[1]:
            # Extract just the suggested markdown file
            markdown_block = ai_response.split("```markdown", 1)[1].split("```", 1)[0].strip()
            has_suggested_config = True
            
        return JsonResponse({
            'reply': ai_response,
            'has_suggested_config': has_suggested_config,
            'suggested_config': markdown_block
        })
        
    except Exception as e:
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

@csrf_exempt
@staff_member_required
@require_http_methods(["POST"])
def apply_changes_view(request):
    """Apply the AI-suggested changes to the site configuration"""
        
    try:
        data = json.loads(request.body)
        new_config = data.get('config', '')
        
        if not new_config:
            return JsonResponse({'error': 'No configuration provided'}, status=400)
            
        # Save the new configuration to site_config.md
        config_path = os.path.join(settings.BASE_DIR, 'site_config.md')
        with open(config_path, 'w') as f:
            f.write(new_config)
            
        # Update the database from the file
        call_command('update_site_config')
        
        return JsonResponse({'success': True, 'message': 'Configuration updated successfully'})
    except Exception as e:
        return JsonResponse({'error': f"Error applying changes: {str(e)}"}, status=500)