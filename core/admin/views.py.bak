"""
Custom admin views for AI-powered site configuration editor.
"""
import os
import json
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

@staff_member_required
def ai_editor_view(request):
    """Renders the AI editor interface"""
    config = SiteConfig.get()
    config_dict = config.to_dict()
    
    # Convert the dictionary to a readable formatted string for the editor
    import json
    current_config = json.dumps(config_dict, indent=2)
    
    # Check if Anthropic API key is configured in settings
    api_key_configured = bool(settings.ANTHROPIC_API_KEY)
    
    # Debug output
    print(f"AI Editor View: Settings API key configured: {api_key_configured}")
    
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
    Handles generation of configuration changes using the Anthropic Claude API.
    
    This view takes a user request message, combines it with the current site configuration,
    and sends it to the Anthropic Claude API to generate updated JSON configuration.
    
    Endpoint: /ai_config/
    Method: POST
    Request Format:
        {
            "message": "The user request message (e.g., 'Change the title to Mick Blog')"
        }
    Response Format:
        {
            "config": JSON object with updated site configuration
        }
    Or for errors:
        {
            "error": "Error message",
            "status_code": 500,
            "error_type": "api_error",
            "detail": "Additional error details"
        }
    """
    # Step 1: Retrieve the API key from settings
    api_key = settings.ANTHROPIC_API_KEY
    
    # Verify API key is available before proceeding
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Step 2: Parse the request body to get the user message
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Get the current site configuration as a dictionary
        config = SiteConfig.get()
        config_dict = config.to_dict()
        current_config = json.dumps(config_dict, indent=2)
        
        # Step 3: Craft a specialized system prompt for generating configuration changes
        system_message = f"""You are a configuration assistant for a Django website. 
Your task is to generate an updated configuration based on the user's request.
The current site configuration is provided as a JSON object:

```json
{current_config}
```

EXTREMELY IMPORTANT INSTRUCTIONS:
1. Output ONLY the updated JSON configuration with the requested changes applied
2. Do NOT include any explanations, markdown formatting, or code blocks
3. Your output must be valid JSON that can be parsed with json.loads()
4. Maintain the exact same structure as the original configuration
5. Only modify the specific fields mentioned in the user request
6. For all other fields, keep their original values
7. DO NOT remove any fields from the original configuration
8. DO NOT add any fields that weren't in the original configuration

For example, if the user asks to change the site title, you should return the entire config object 
with ONLY the title field modified in the site_info section.

Always validate that your response is proper JSON before returning it.
"""

        # Step 4: Prepare the message array with the user's request
        api_messages = [
            {"role": "user", "content": f"Update the site configuration with this change: {user_message}"}
        ]
        
        # Step 5: Set up API request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01"
        }
        
        # Step 6: Prepare the request body with parameters optimized for configuration generation
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.2,  # Lower temperature for more deterministic output
            "messages": api_messages,
            "system": system_message
        }
        
        # Log the request details for debugging
        print(f"CONFIG GENERATION: Requesting updated config for: {user_message}")
        
        # Step 7: Make the API request with comprehensive error handling
        try:
            # Log essential request information
            print(f"CONFIG GENERATION: Sending request to Anthropic API")
            print(f"CONFIG GENERATION: Using model: {request_body['model']}")
            print(f"CONFIG GENERATION: User message: {user_message}")
            
            # Send the API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body,
                timeout=60
            )
            
            # Log response status immediately
            print(f"CONFIG GENERATION: Received response with status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            error_detail = str(e)
            print(f"CONFIG GENERATION: Request exception: {error_detail}")
            
            return JsonResponse({
                'error': f"API connection error: {error_detail}",
                'detail': "Failed to connect to the Anthropic API. Please check your network connection and try again."
            }, status=500)
        
        # Step 8: Process API response with detailed error handling
        if response.status_code != 200:
            # If not a successful response, extract and format error information
            error_message = "Unknown error"
            error_type = "api_error"
            response_text = ""
            
            try:
                # Get the full response text for logging
                response_text = response.text
                print(f"CONFIG GENERATION: Full error response: {response_text}")
                
                # Try to parse the response as JSON
                error_data = response.json()
                print(f"CONFIG GENERATION: JSON error data: {error_data}")
                
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
                print(f"CONFIG GENERATION: Exception while handling error: {str(e)}")
                
            print(f"CONFIG GENERATION: API Error: {error_message}")
            
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
        
        # Clean up the response - remove any markdown formatting if present
        cleaned_response = ai_response.strip()
        
        # If response is wrapped in code blocks, extract the JSON
        if cleaned_response.startswith("```json") or cleaned_response.startswith("```"):
            import re
            matches = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned_response)
            if matches:
                cleaned_response = matches[0].strip()
        
        # Validate that the response is valid JSON
        try:
            # Parse the JSON to ensure it's valid
            updated_config = json.loads(cleaned_response)
            
            # Log successful parsing
            print(f"CONFIG RESPONSE: Successfully parsed JSON response")
            
            # Step 10: Return the validated configuration
            return JsonResponse({'config': updated_config})
            
        except json.JSONDecodeError as e:
            # If the response isn't valid JSON, return an error
            print(f"CONFIG RESPONSE: Invalid JSON in response: {e}")
            return JsonResponse({
                'error': "Invalid JSON in API response",
                'detail': f"The API returned a response that could not be parsed as JSON: {str(e)}"
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
@require_http_methods(["POST"])
def ai_message_view(request):
    """
    Handles API interaction with Claude for conversational responses about site configuration.
    
    This view takes a user message (and optionally message history) and sends it to the
    Anthropic Claude API to get a conversational response about site configuration options.
    
    Endpoint: /ai_message/
    Method: POST
    Request Format:
        {
            "message": "User's question or request",
            "history": [
                {"role": "user", "content": "Previous user message"},
                {"role": "assistant", "content": "Previous assistant response"}
            ]
        }
    Response Format:
        {
            "reply": "Assistant's conversational response"
        }
    Or for errors:
        {
            "error": "Error message",
            "detail": "Additional error details"  // Optional
        }
    """
    # Step 1: Retrieve and validate the API key
    api_key = settings.ANTHROPIC_API_KEY
    
    # Log API key availability for debugging
    print(f"AI Message View: API key available: {bool(api_key)}")
    
    # Verify API key is available
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Step 2: Parse the request body and extract parameters
        data = json.loads(request.body)
        user_message = data.get('message', '')
        message_history = data.get('history', [])
        
        # Get the current site configuration for reference
        config = SiteConfig.get()
        config_dict = config.to_dict()
        current_config = json.dumps(config_dict, indent=2)
        
        # Step 3: Create the system message for conversational responses
        system_message = f"""You are a Django site configuration assistant. 
You help users configure their Django-based personal website.
The current site configuration is shown below (for your reference only):

```json
{current_config}
```

IMPORTANT INSTRUCTIONS:
1. You are helping the user make changes to their site configuration
2. Be specific about what fields the user can change and what values are valid
3. Keep your responses conversational, helpful, and to the point
4. Explain where changes would be visible on the site
5. Do NOT include the complete configuration in your responses
6. If the user asks to make specific changes, tell them what fields would be updated

Example response:
"I'd update the site title from 'Mick's Blog' to 'VibeBlog'. This change would appear in the browser title bar and anywhere the site title is displayed."
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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01"
        }
        
        # Step 6: Prepare request body
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.7,  # Higher temperature for more creative conversation
            "messages": api_messages,
            "system": system_message
        }
        
        # Log request info
        print(f"AI_MESSAGE: Sending request to Anthropic API")
        print(f"AI_MESSAGE: Using model: {request_body['model']}")
        print(f"AI_MESSAGE: Message history length: {len(message_history)}")
        print(f"AI_MESSAGE: Current user message: {user_message}")
        
        # Step 7: Make the API request with error handling
        try:
            # Send the API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body,
                timeout=60
            )
            
            # Log response status
            print(f"AI_MESSAGE: Received response with status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            error_detail = str(e)
            print(f"AI_MESSAGE: Request exception: {error_detail}")
            
            return JsonResponse({
                'error': f"API connection error: {error_detail}",
                'detail': "Failed to connect to the Anthropic API. Please check your network connection."
            }, status=500)
        
        # Step 8: Handle non-successful API responses
        if response.status_code != 200:
            error_message = "Unknown error"
            
            try:
                # Try to extract error details from the response
                response_text = response.text
                error_data = response.json()
                
                # Extract structured error information if available
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                    else:
                        error_message = str(error_data['error'])
            except Exception as e:
                error_message = f"Error parsing API response: {str(e)}"
                
            print(f"AI_MESSAGE: API Error: {error_message}")
            
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'detail': "The Anthropic API returned an error."
            }, status=500)
        
        # Step 9: Process the successful API response
        try:
            response_data = response.json()
            ai_response = response_data['content'][0]['text']
            
            # For conversation mode, just return the AI's reply directly
            return JsonResponse({
                'reply': ai_response
            })
                
        except Exception as e:
            # Handle any errors while processing the API response
            print(f"Error processing response: {e}")
            traceback.print_exc()
            return JsonResponse({
                'error': f"Error processing response: {str(e)}",
                'detail': "The API returned a successful response, but there was an error processing it."
            }, status=500)
            
    except Exception as e:
        # Catch-all exception handler
        print(f"Error in ai_message_view: {str(e)}")
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