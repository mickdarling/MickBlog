"""
Custom admin views for AI-powered site configuration editor.
"""
import os
import json
import re
import requests
import traceback
import reversion
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.management import call_command
from core.models import SiteConfig
from core.utils import reload_env_settings, get_anthropic_api_key

@staff_member_required
def ai_editor_view(request):
    """Renders the AI editor interface"""
    config = SiteConfig.get()
    config_dict = config.to_dict()
    
    # Convert the dictionary to a readable formatted string for the editor
    import json
    current_config = json.dumps(config_dict, indent=2)
    
    # Check if Anthropic API key is configured using our robust method
    api_key = get_anthropic_api_key()
    api_key_configured = bool(api_key)
    
    # Debug output
    print(f"AI Editor View: API key configured: {api_key_configured}")
    if api_key_configured:
        print(f"AI Editor View: API key starts with: {api_key[:5]}")
    
    context = {
        'title': 'AI Site Configuration Editor',
        'config': config,
        'current_config': current_config,
        'api_key_configured': api_key_configured,
        'debug_info': {
            'settings_key_present': api_key_configured,
            'model_key_present': False,
            'api_key_first_chars': settings.ANTHROPIC_API_KEY[:5] if settings.ANTHROPIC_API_KEY else 'None'
        }
    }
    return render(request, 'admin/core/ai_editor.html', context)

@csrf_exempt
@staff_member_required
def test_json_view(request):
    """Simple test endpoint that just returns JSON"""
    print("TEST_JSON_VIEW called successfully")
    return JsonResponse({'success': True, 'message': 'Test JSON response'})

@csrf_exempt
@staff_member_required
def mock_ai_config_view(request):
    """A simplified version of the config endpoint that doesn't use the AI API"""
    print("MOCK_AI_CONFIG_VIEW called - Beginning processing")
    
    try:
        # Try to parse request body
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            print(f"Received message: {user_message}")
        except json.JSONDecodeError:
            print("Failed to parse JSON request body")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        
        # Get the current config
        config = SiteConfig.get()
        current_config = config.export_to_markdown()
        print(f"Got current config: {len(current_config)} chars")
        
        # Create a modified config based on the user message
        modified_config = current_config
        
        # Simple rule-based changes without using AI
        user_message_lower = user_message.lower()
        
        # Handle title changes
        if 'title' in user_message_lower:
            current_title = None
            new_title = None
            
            # Extract current title from config
            import re
            title_match = re.search(r'title: ([^\n]+)', current_config)
            if title_match:
                current_title = title_match.group(1)
            
            # Determine new title
            if 'mick' in user_message_lower or "mick's" in user_message_lower:
                new_title = "Mick's Blog"
            elif 'vibe' in user_message_lower:
                new_title = "Vibe Blog"
            elif 'awesome' in user_message_lower:
                new_title = "Awesome Blog"
            elif 'cool' in user_message_lower:
                new_title = "Cool Blog"
                
            # Apply the change if we found both current and new titles
            if current_title and new_title:
                print(f"Changing title from '{current_title}' to '{new_title}'")
                modified_config = modified_config.replace(f"title: {current_title}", f"title: {new_title}")
                
        # Handle tagline changes
        if 'tagline' in user_message_lower:
            if 'awesome' in user_message_lower:
                print("Detected request to change tagline")
                modified_config = modified_config.replace(
                    "tagline: Projects, Posts, Resume, and Contact Info", 
                    "tagline: Awesome Projects, Cool Posts, and More!"
                )
                
        # Handle color changes
        if 'color' in user_message_lower:
            if 'primary' in user_message_lower and 'red' in user_message_lower:
                print("Detected request to change primary color to red")
                modified_config = modified_config.replace(
                    "primary_color: '#007bff'", 
                    "primary_color: '#ff0000'"
                )
            elif 'primary' in user_message_lower and 'green' in user_message_lower:
                print("Detected request to change primary color to green")
                modified_config = modified_config.replace(
                    "primary_color: '#007bff'", 
                    "primary_color: '#00ff00'"
                )
        
        print(f"Modified config created: {len(modified_config)} chars")
        print(f"First 100 chars: {modified_config[:100]}")
        
        # Return the modified config
        return JsonResponse({'config': modified_config})
            
    except Exception as e:
        print(f"Error in mock_ai_config_view: {str(e)}")
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

@csrf_exempt
@staff_member_required
@require_http_methods(["POST"])
def ai_config_view(request):
    """
    Combined endpoint that handles both natural language responses and config generation.
    
    This view takes a user request message, combines it with the current site configuration,
    and sends it to the Anthropic Claude API to generate a combined response with both
    natural language explanation and JSON configuration.
    
    Endpoint: /ai_config/
    Method: POST
    Request Format:
        {
            "message": "The user request message (e.g., 'Change the title to Mick Blog')",
            "history": Optional array of previous message history
        }
    Response Format:
        {
            "reply": "Natural language response explaining the changes",
            "config": "JSON configuration string with the changes applied"
        }
    Or for errors:
        {
            "error": "Error message",
            "detail": "Additional error details"
        }
    """
    # Step 1: Get the API key with multiple fallbacks
    api_key = get_anthropic_api_key()
    
    # Verify API key is available before proceeding
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Step 2: Parse the request body to get the user message and optional history
        data = json.loads(request.body)
        user_message = data.get('message', '')
        message_history = data.get('history', [])
        
        # Get the current site configuration as a dictionary
        config = SiteConfig.get()
        config_dict = config.to_dict()
        current_config = json.dumps(config_dict, indent=2)
        
        # Step 3: Craft a specialized system prompt that requests BOTH a natural language response
        # and a JSON configuration in a structured format
        system_message = f"""You are a configuration assistant for a Django website.
Your task is to help users update their site configuration using both natural language and JSON.

The current site configuration is provided as a JSON object:

```json
{current_config}
```

EXTREMELY IMPORTANT INSTRUCTIONS:
1. First, determine if the user's request is asking for a specific configuration change.
   - If they are asking for a change (e.g., "Change the title to X", "Make the colors more vibrant"), provide BOTH explanation and JSON sections
   - If they are just saying hello, testing, or asking a question without requesting changes, ONLY provide the explanation section

2. For requests that DO need configuration changes, format your response like this:
```explanation
Your natural language explanation here, speaking directly to the user. Be concise but helpful.
```

```json
{{
  "site_info": {{
    "title": "Example Title",
    ...
  }},
  ...
}}
```

3. For requests that do NOT need configuration changes, ONLY include the explanation:
```explanation
Your response explaining that no changes are needed, or answering their question, or greeting them back.
```

4. For the JSON section (when needed):
   - Include the ENTIRE configuration object, with all fields
   - Only modify the specific fields mentioned in the user's request
   - Maintain the exact same structure as the original configuration
   - Ensure the JSON is valid and properly formatted

5. For the explanation section:
   - Be concise but friendly and helpful
   - For change requests, explain what you're changing and why
   - Mention where the changes will be visible on the site
   - Keep this section under 150 words

Example responses:

For a change request:
```explanation
I've updated the site title to "Ethereal Visions" to give it a more dreamy, otherworldly feel. This change will be visible in the browser tab, the site header, and anywhere else the title is displayed. I've kept the rest of your site configuration unchanged.
```

```json
{{
  "site_info": {{
    "title": "Ethereal Visions",
    ...rest of unchanged config...
  }}
}}
```

For a non-change request like "Hello" or "Test":
```explanation
Hello! I'm here to help you update your site configuration. If you'd like to make changes to your site, you can ask me to modify specific elements like the title, colors, tagline, or other aspects of your site. Just let me know what you'd like to change.
```
"""

        # Step 4: Prepare the message array with conversation history
        api_messages = []
        
        # Add previous conversation history if available
        for msg in message_history:
            # Skip system messages as they're not supported in this format
            if msg["role"] == "system":
                continue
                
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            
        # Add the current user message
        api_messages.append({"role": "user", "content": user_message})
        
        # Step 5: Set up API request headers
        # Make sure there are no trailing whitespaces or quotes in the API key
        clean_api_key = api_key.strip().strip('"\'')
        
        # Current documentation recommends using both Authorization and x-api-key headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_api_key}",
            "anthropic-version": "2023-06-01",
            "x-api-key": clean_api_key  # Add this for compatibility with different API versions
        }
        
        # Debug information about headers
        print(f"COMBINED_AI: Authorization header length: {len(f'Bearer {clean_api_key}')}")
        print(f"COMBINED_AI: Header starts with: Bearer {clean_api_key[:7]}...")
        
        # Step 6: Prepare the request body with parameters optimized for configuration generation
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.2,  # Lower temperature for more deterministic output
            "messages": api_messages,
            "system": system_message
        }
        
        # Log the request details for debugging
        print(f"COMBINED_AI: Processing request: {user_message}")
        
        # Step 7: Make the API request with comprehensive error handling
        try:
            # Log essential request information
            print(f"COMBINED_AI: Sending request to Anthropic API")
            print(f"COMBINED_AI: Using model: {request_body['model']}")
            print(f"COMBINED_AI: User message: {user_message}")
            
            # Log the API key being used (first 5 chars only for security)
            print(f"COMBINED_AI: Using API key starting with: {api_key[:5]}")
            
            # Send the API request to the most current endpoint
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body,
                timeout=60
            )
            
            # Log response status immediately
            print(f"COMBINED_AI: Received response with status code: {response.status_code}")
            
            # Log the response text if there's an error
            if response.status_code != 200:
                print(f"COMBINED_AI: Error response: {response.text[:200]}...")
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            error_detail = str(e)
            print(f"COMBINED_AI: Request exception: {error_detail}")
            
            return JsonResponse({
                'error': f"API connection error: {error_detail}",
                'detail': "Failed to connect to the Anthropic API. Please check your network connection and try again."
            }, status=500)
        
        # Step 8: Process API response with detailed error handling
        if response.status_code != 200:
            # If not a successful response, extract and format error information
            error_message = "Unknown error"
            error_type = "api_error"
            
            try:
                # Get the full response text for logging
                response_text = response.text
                print(f"COMBINED_AI: Full error response: {response_text}")
                
                # Try to parse the response as JSON
                error_data = response.json()
                print(f"COMBINED_AI: JSON error data: {error_data}")
                
                # Extract structured error information if available
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                        error_type = error_data['error'].get('type', 'api_error')
                    else:
                        error_message = str(error_data['error'])
                elif 'type' in error_data and 'message' in error_data:
                    error_message = f"{error_data.get('type')}: {error_data.get('message')}"
                    error_type = error_data.get('type', 'api_error')
            except Exception as e:
                # Catch-all for any error handling issues
                error_message = f"Failed to parse error response: {str(e)}"
                print(f"COMBINED_AI: Exception while handling error: {str(e)}")
                
            print(f"COMBINED_AI: API Error: {error_message}")
            
            # Return a comprehensive error response with all available information
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'status_code': response.status_code,
                'error_type': error_type,
                'detail': "The Anthropic API returned an error. Please check the API key and try again."
            }, status=500)
        
        # Step 9: Extract and process the successful API response
        response_data = response.json()
        ai_response = response_data['content'][0]['text']
        print(f"COMBINED_AI: Raw response: {ai_response[:100]}...")
        
        # Step 10: Parse the structured response to extract explanation and configuration
        explanation = ""
        config_json = ""
        
        # Use regex to extract the explanation section
        explanation_match = re.search(r'```explanation\s*([\s\S]*?)\s*```', ai_response)
        if explanation_match:
            explanation = explanation_match.group(1).strip()
            print(f"COMBINED_AI: Extracted explanation: {explanation[:50]}...")
        else:
            print(f"COMBINED_AI: No explanation section found, using full response as explanation")
            explanation = ai_response
        
        # Use regex to extract the JSON section
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', ai_response)
        if json_match:
            config_json = json_match.group(1).strip()
            print(f"COMBINED_AI: Extracted JSON: {config_json[:50]}...")
        else:
            print(f"COMBINED_AI: No JSON section found - possibly no changes needed")
            
            # For cases where the AI doesn't understand what to change or no changes are needed,
            # return only the explanation without a 500 error
            return JsonResponse({
                'reply': explanation,
                'config': None,  # No config changes
                'no_changes': True  # Flag to indicate no changes were made
            })
        
        # Step 11: Validate the extracted JSON
        try:
            # Parse the JSON to ensure it's valid
            parsed_config = json.loads(config_json)
            
            # For debugging, validate the configuration has the required structure
            # Every config should have a site_info section
            if not isinstance(parsed_config, dict) or 'site_info' not in parsed_config:
                print(f"COMBINED_AI: Warning - JSON response missing site_info section")
            
            # Return both the explanation and configuration
            return JsonResponse({
                'reply': explanation,
                'config': config_json
            })
            
        except json.JSONDecodeError as e:
            # If the response isn't valid JSON, return an error
            print(f"COMBINED_AI: Invalid JSON in response: {e}")
            return JsonResponse({
                'error': "Invalid JSON in API response",
                'detail': f"The API returned a response with invalid JSON: {str(e)}"
            }, status=500)
            
    except Exception as e:
        # Catch-all exception handler for any unhandled errors
        print(f"Error in ai_config_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error: {str(e)}",
            'detail': "An unexpected error occurred while processing your request."
        }, status=500)


@csrf_exempt
@staff_member_required
def mock_apply_changes_view(request):
    """Simple version of apply changes that doesn't require authentication"""
    print("MOCK_APPLY_CHANGES_VIEW called")
    
    try:
        try:
            data = json.loads(request.body)
            new_config = data.get('config', '')
            print(f"Received config: {len(new_config)} chars")
        except json.JSONDecodeError:
            print("Failed to parse JSON request body")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        
        if not new_config:
            print("No configuration provided")
            return JsonResponse({'error': 'No configuration provided'}, status=400)
            
        # Save the new configuration to site_config.md
        config_path = os.path.join(settings.BASE_DIR, 'site_config.md')
        print(f"Saving to {config_path}")
        
        with open(config_path, 'w') as f:
            f.write(new_config)
            
        # Update the database from the file
        print("Calling update_site_config")
        call_command('update_site_config')
        
        print("Configuration applied successfully")
        return JsonResponse({'success': True, 'message': 'Configuration updated successfully'})
    except Exception as e:
        print(f"Error in mock_apply_changes_view: {str(e)}")
        return JsonResponse({'error': f"Error applying changes: {str(e)}"}, status=500)

@csrf_exempt
@staff_member_required
@require_http_methods(["POST"])
def apply_changes_view(request):
    """
    Applies the AI-suggested changes to the site configuration by
    directly updating the database model from JSON data.
    
    Endpoint: /apply_changes/
    Method: POST
    Request Format:
        {
            "config": JSON object with site configuration data
        }
    Response Format:
        {
            "success": true,
            "message": "Configuration updated successfully"
        }
    Or for errors:
        {
            "error": "Error message",
            "detail": "Additional error details"  // Optional
        }
    """
    print("APPLY_CHANGES_VIEW called")
        
    try:
        # Step 1: Parse and validate the request data
        data = json.loads(request.body)
        new_config_json = data.get('config', '')
        
        # Ensure we have a configuration to apply
        if not new_config_json:
            return JsonResponse({
                'error': 'No configuration provided',
                'detail': 'The request must include a configuration object.'
            }, status=400)
        
        # Parse the config JSON if it's a string
        if isinstance(new_config_json, str):
            try:
                new_config_data = json.loads(new_config_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON configuration',
                    'detail': 'The configuration must be a valid JSON object.'
                }, status=400)
        else:
            new_config_data = new_config_json
            
        # Get the current configuration
        config = SiteConfig.get()
        
        # Update configuration with reversion tracking
        with reversion.create_revision():
            # Step 2: Update fields from the JSON data
            try:
                # Basic site info
                if 'site_info' in new_config_data:
                    site_info = new_config_data['site_info']
                    config.title = site_info.get('title', config.title)
                    config.tagline = site_info.get('tagline', config.tagline)
                    config.brand = site_info.get('brand', config.brand)
                    config.footer_text = site_info.get('footer_text', config.footer_text)
                    config.meta_description = site_info.get('meta_description', config.meta_description)
                
                # Colors
                if 'colors' in new_config_data:
                    colors = new_config_data['colors']
                    config.primary_color = colors.get('primary_color', config.primary_color)
                    config.secondary_color = colors.get('secondary_color', config.secondary_color)
                
                # Content
                if 'content' in new_config_data:
                    content = new_config_data['content']
                    if 'about_text' in content:
                        config.about_text = content['about_text']
                
                # Contact info
                if 'contact' in new_config_data:
                    contact = new_config_data['contact']
                    config.email = contact.get('email', config.email)
                    config.phone = contact.get('phone', config.phone)
                    config.address = contact.get('address', config.address)
                
                # Social media
                if 'social' in new_config_data:
                    social = new_config_data['social']
                    config.github_url = social.get('github_url', config.github_url)
                    config.linkedin_url = social.get('linkedin_url', config.linkedin_url)
                    config.twitter_url = social.get('twitter_url', config.twitter_url)
                    config.facebook_url = social.get('facebook_url', config.facebook_url)
                    config.instagram_url = social.get('instagram_url', config.instagram_url)
                    config.bluesky_url = social.get('bluesky_url', config.bluesky_url)
                
                # Analytics
                if 'analytics' in new_config_data:
                    analytics = new_config_data['analytics']
                    config.google_analytics_id = analytics.get('google_analytics_id', config.google_analytics_id)
                
                # Appearance
                if 'appearance' in new_config_data:
                    appearance = new_config_data['appearance']
                    config.custom_css = appearance.get('custom_css', config.custom_css)
                
                # System
                if 'system' in new_config_data:
                    system = new_config_data['system']
                    config.maintenance_mode = system.get('maintenance_mode', config.maintenance_mode)
                
                # Step 3: Save the configuration to the database
                config.save()
                
                # Set revision metadata
                if request.user.is_authenticated:
                    reversion.set_user(request.user)
                reversion.set_comment("Updated via AI Editor")
                
                # Step 4: Export custom CSS to file
                if config.custom_css:
                    config.save_custom_css()
                
                print("Configuration successfully updated in database")
                
            except Exception as e:
                print(f"Error updating configuration: {str(e)}")
                traceback.print_exc()
                return JsonResponse({
                    'error': f"Error updating configuration: {str(e)}",
                    'detail': "Failed to update the site configuration in the database."
                }, status=500)
        
        # Step 5: Return success response
        return JsonResponse({
            'success': True, 
            'message': 'Configuration updated successfully.'
        })
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"JSON parsing error: {str(e)}")
        return JsonResponse({
            'error': f"Invalid JSON in request: {str(e)}",
            'detail': "The request body must be valid JSON with a 'config' field."
        }, status=400)
    except Exception as e:
        # Catch-all exception handler
        print(f"Error in apply_changes_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error applying changes: {str(e)}",
            'detail': "An unexpected error occurred while updating the configuration."
        }, status=500)