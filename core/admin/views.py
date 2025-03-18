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
    settings_key = bool(settings.ANTHROPIC_API_KEY)
    model_key = bool(config.anthropic_api_key)
    
    # Only enable the editor if API key is properly configured
    api_key_configured = settings_key or model_key
    
    # Debug output
    print(f"AI Editor View: Settings API key configured: {settings_key}")
    print(f"AI Editor View: Model API key configured: {model_key}")
    print(f"AI Editor View: API key flag manually set to: {api_key_configured}")
    print(f"AI Editor View: Actual API key: {config.anthropic_api_key[:5]}... (truncated)")
    
    context = {
        'title': 'AI Site Configuration Editor',
        'config': config,
        'current_config': current_config,
        'api_key_configured': api_key_configured,
        'debug_info': {
            'settings_key_present': settings_key,
            'model_key_present': model_key,
            'api_key_first_chars': config.anthropic_api_key[:5] if config.anthropic_api_key else 'None'
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
    Handles generation of configuration files using the Anthropic Claude API.
    
    This view takes a user request message, combines it with the current site configuration,
    and sends it to the Anthropic Claude API to generate a modified configuration file.
    The API response is then validated and returned as JSON.
    
    Endpoint: /ai_config/
    Method: POST
    Request Format:
        {
            "message": "The user request message (e.g., 'Change the title to Mick Blog')"
        }
    Response Format:
        {
            "config": "Generated configuration file content"
        }
    Or for errors:
        {
            "error": "Error message",
            "status_code": 500,
            "error_type": "api_error",
            "detail": "Additional error details"
        }
    """
    # Step 1: Retrieve the API key from settings or model, preferring settings
    config = SiteConfig.get()
    settings_key = settings.ANTHROPIC_API_KEY
    model_key = config.anthropic_api_key
    api_key = settings_key or model_key
    
    # Verify API key is available before proceeding
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add an API key in the site configuration or environment variables.'
        }, status=500)
    
    try:
        # Step 2: Parse the request body to get the user message
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Get the current site configuration
        config = SiteConfig.get()
        current_config = config.export_to_markdown()
        
        # Step 3: Craft a specialized system prompt for generating configuration changes
        # This prompt is crucial for getting the exact format we need from the API
        system_message = f"""You are a YAML configuration file generator for a Django website. 
Your task is to generate a complete configuration file based on the user's request.
The current site configuration template is:

```markdown
{current_config}
```

EXTREMELY IMPORTANT INSTRUCTIONS:
1. Output ONLY the raw updated configuration file with the requested changes applied
2. DO NOT add any explanation, comments, or introduction text
3. DO NOT use markdown code blocks in your output - just return the raw file content
4. ALWAYS begin your output with "# Site Configuration Template"
5. Include ALL sections from the original file EXACTLY as they appear
6. Only modify the SPECIFIC fields mentioned in the user request
7. Maintain EXACT same formatting, indentation, and structure as the original file
8. For YAML fields, preserve the exact same quoting style as the original

Example user request: "Change the site title to Mick Blog"
Example response:
# Site Configuration Template

This markdown file allows you to easily customize the content, style, and configuration of your MickBlog site. Edit the sections below and migrate the database to apply changes.

## Site Information

```yaml
brand: MB
footer_text: "© 2025 Your Name. All rights reserved."
meta_description: Personal blog and portfolio site showcasing blog posts, projects, resume, and contact information.
tagline: Projects, Posts, Resume, and Contact Info
title: Mick Blog

```

[... rest of file unchanged ...]
"""

        # Step 4: Prepare the message array with the user's request
        api_messages = [
            {"role": "user", "content": f"Update the configuration file with this change: {user_message}"}
        ]
        
        # Step 5: Set up API request headers with both authorization formats
        # We include both formats for compatibility with different API versions
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,  # For backward compatibility with older API versions
            "Authorization": f"Bearer {api_key}", # Current bearer token format
            "anthropic-version": "2023-06-01" # Specific API version for stability
        }
        
        # Step 6: Prepare the request body with parameters optimized for configuration generation
        request_body = {
            "model": "claude-3-sonnet-20240229", # Specific model version for consistent results
            "max_tokens": 4000,  # Generous token limit to ensure full config is returned
            "temperature": 0.3,  # Lower temperature for more deterministic, predictable output
            "messages": api_messages,
            "system": system_message
        }
        
        # Log the request details for debugging
        print(f"CONFIG GENERATION: Requesting updated config for: {user_message}")
        
        # Step 7: Make the API request with comprehensive error handling
        try:
            # Log detailed request information before sending
            print(f"CONFIG GENERATION: Sending request to Anthropic API with key length: {len(api_key)}")
            print(f"CONFIG GENERATION: Request headers: {headers}")
            print(f"CONFIG GENERATION: Using model: {request_body['model']}")
            print(f"CONFIG GENERATION: System message length: {len(system_message)}")
            print(f"CONFIG GENERATION: User message: {user_message}")
            
            # Send the API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body,
                timeout=60  # Increased timeout for reliability
            )
            
            # Log response status immediately
            print(f"CONFIG GENERATION: Received response with status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors (timeouts, connection failures, etc.)
            error_detail = str(e)
            print(f"CONFIG GENERATION: Request exception: {error_detail}")
            
            # Return a structured error response with helpful details
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
            except ValueError as e:
                # Handle non-JSON responses
                error_message = f"Non-JSON error response: {response_text[:200]}"
                print(f"CONFIG GENERATION: Failed to parse JSON: {str(e)}")
            except Exception as e:
                # Catch-all for any other error handling issues
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
        
        # Clean up and validate the response format
        cleaned_response = ai_response.strip()
        print(f"CONFIG RESPONSE: {cleaned_response[:100]}...")
        
        # Ensure the response has the correct header format
        if not cleaned_response.startswith("# Site Configuration"):
            print("WARNING: Adding missing header to config response")
            cleaned_response = "# Site Configuration Template\n\n" + cleaned_response
        
        # Step 10: Return the validated configuration
        return JsonResponse({'config': cleaned_response})
            
    except Exception as e:
        # Catch-all exception handler for any unhandled errors
        print(f"Error in ai_config_view: {str(e)}")
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
    It can also generate configuration files directly if the generate_config flag is set.
    
    Endpoint: /ai_message/
    Method: POST
    Request Format:
        {
            "message": "User's question or request",
            "history": [
                {"role": "user", "content": "Previous user message"},
                {"role": "assistant", "content": "Previous assistant response"}
            ],
            "generate_config": false  // Optional boolean to generate config instead of conversation
        }
    Response Format:
        {
            "reply": "Assistant's conversational response"
        }
    Or for config generation:
        {
            "config": "Generated configuration file content"
        }
    Or for errors:
        {
            "error": "Error message",
            "status_code": 500,  // Optional
            "error_type": "api_error",  // Optional
            "detail": "Additional error details"  // Optional
        }
    """
    # Step 1: Retrieve and validate the API key
    config = SiteConfig.get()
    settings_key = settings.ANTHROPIC_API_KEY
    model_key = config.anthropic_api_key
    api_key = settings_key or model_key
    
    # Log API key availability for debugging
    print(f"AI Message View: Settings API key available: {bool(settings_key)}")
    print(f"AI Message View: Model API key available: {bool(model_key)}")
    print(f"AI Message View: Using API key: {api_key[:5]}... (truncated)")
    
    # Verify API key is available
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add an API key in the site configuration or environment variables.'
        }, status=500)
    
    try:
        # Step 2: Parse the request body and extract parameters
        data = json.loads(request.body)
        user_message = data.get('message', '')
        message_history = data.get('history', [])
        generate_config = data.get('generate_config', False)
        
        # Get the current site configuration for reference
        config = SiteConfig.get()
        current_config = config.export_to_markdown()
        
        # Step 3: Create the appropriate system message based on the request type
        if generate_config:
            # System message optimized for configuration file generation
            system_message = f"""You are a Django site configuration assistant. 
Your task is to generate a complete configuration file based on the user's request.
The current site configuration is shown below:

```markdown
{current_config}
```

IMPORTANT FORMATTING INSTRUCTIONS:
1. Output ONLY the complete markdown file without any introduction or explanation
2. Make sure to include the ENTIRE file content, with the user's requested changes applied
3. Keep ALL sections even if unchanged, including the '# Site Configuration Template' header
4. Maintain the exact same structure and format as the original file
5. The output should be a direct drop-in replacement for site_config.md
6. Do not add any text before or after the markdown file - just output the raw file content

YOU MUST START WITH: # Site Configuration Template
"""
        else:
            # System message optimized for conversational responses
            system_message = f"""You are a Django site configuration assistant. 
You help edit the site_config.md file for a Django blog site.
The current site configuration is shown below (for your reference only):

```markdown
{current_config}
```

IMPORTANT FORMATTING INSTRUCTIONS:
1. Do NOT include the complete configuration file in your responses
2. Instead, explain what changes you would make to fulfill the user's request
3. Be specific about what fields you would change and to what values
4. Keep your responses conversational and helpful

Example response:
"I'd update the site title from 'Mick's Blog' to 'VibeBlog'. This change would appear in the browser title bar and anywhere the site title is displayed."

Be specific and helpful with your suggestions, but do NOT include markdown code blocks with the full configuration.
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
        
        # Step 5: Set up API request headers with both authorization formats
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,  # For backward compatibility with older versions
            "Authorization": f"Bearer {api_key}",  # Current standard bearer token format
            "anthropic-version": "2023-06-01"  # Specific API version for stability
        }
        
        # Step 6: Prepare request body with parameters optimized based on request type
        request_body = {
            "model": "claude-3-sonnet-20240229",  # Specific model version for consistency
            "max_tokens": 4000,  # Generous token limit for comprehensive responses
            "temperature": 0.7,  # Higher temperature for more creative, natural conversation
            "messages": api_messages,
            "system": system_message
        }
        
        # Log request type and key information
        print(f"API Request type: {'CONFIG GENERATION' if generate_config else 'CONVERSATION'}")
        print(f"API Key format: {api_key[:5]}... (length: {len(api_key)})")
        
        # Step 7: Make the API request with comprehensive error handling
        try:
            # Log detailed request information before sending
            print(f"AI_MESSAGE: Sending request to Anthropic API with key length: {len(api_key)}")
            print(f"AI_MESSAGE: Using model: {request_body['model']}")
            print(f"AI_MESSAGE: System message length: {len(system_message)}")
            print(f"AI_MESSAGE: Message history length: {len(message_history)}")
            print(f"AI_MESSAGE: Current user message: {user_message}")
            
            # Send the API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_body,
                timeout=60  # Increased timeout for reliability
            )
            
            # Log response status immediately
            print(f"AI_MESSAGE: Received response with status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors with detailed logging
            error_detail = str(e)
            print(f"AI_MESSAGE: Request exception: {error_detail}")
            
            # Return a structured error response with helpful details
            return JsonResponse({
                'error': f"API connection error: {error_detail}",
                'detail': "Failed to connect to the Anthropic API. Please check your network connection and try again."
            }, status=500)
        
        # Step 8: Handle non-successful API responses with detailed error extraction
        if response.status_code != 200:
            error_message = "Unknown error"
            error_type = "api_error"
            response_text = ""
            
            try:
                # Get full response text for comprehensive logging
                response_text = response.text
                print(f"AI_MESSAGE: Full error response: {response_text}")
                
                # Try to parse response as JSON for structured error details
                error_data = response.json()
                print(f"AI_MESSAGE: JSON error data: {error_data}")
                
                # Extract the most useful error information in various API response formats
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                        error_type = error_data['error'].get('type', 'api_error')
                    else:
                        error_message = str(error_data['error'])
                elif 'type' in error_data and 'message' in error_data:
                    error_message = f"{error_data.get('type')}: {error_data.get('message')}"
                    error_type = error_data.get('type', 'api_error')
            except ValueError as e:
                # Handle non-JSON responses
                error_message = f"Non-JSON error response: {response_text[:200]}"
                print(f"AI_MESSAGE: Failed to parse JSON: {str(e)}")
            except Exception as e:
                # Catch-all for any other error handling issues
                error_message = f"Failed to parse error response: {str(e)}"
                print(f"AI_MESSAGE: Exception while handling error: {str(e)}")
                
            print(f"AI_MESSAGE: API Error: {error_message}")
            
            # Return a comprehensive error response with all available information
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'status_code': response.status_code,
                'error_type': error_type,
                'detail': "The Anthropic API returned an error. Please check the API key and try again."
            }, status=500)
        
        # Step 9: Process the successful API response
        try:
            response_data = response.json()
            ai_response = response_data['content'][0]['text']
            
            # Handle the response differently based on the request type
            if generate_config:
                # For config generation, clean up and validate the response format
                cleaned_response = ai_response.strip()
                
                # Log the response for debugging
                print(f"CONFIG GENERATION RESPONSE: {cleaned_response[:100]}...")
                
                # Validate and fix the response format if needed
                if not cleaned_response.startswith("# Site Configuration"):
                    print("WARNING: Config response doesn't start with expected header")
                    
                    # If the response is wrapped in markdown code blocks, extract the content
                    if "```" in cleaned_response:
                        import re
                        matches = re.findall(r'```(?:markdown)?\s*([\s\S]*?)\s*```', cleaned_response)
                        if matches:
                            cleaned_response = matches[0].strip()
                            print(f"Extracted from code blocks: {cleaned_response[:100]}...")
                    
                    # If still not formatted correctly, add the required header
                    if not cleaned_response.startswith("# Site Configuration"):
                        print("Adding header to config response")
                        cleaned_response = "# Site Configuration Template\n\n" + cleaned_response
                
                # Return the properly formatted configuration file
                return JsonResponse({
                    'config': cleaned_response
                })
            else:
                # For conversation mode, just return the AI's reply directly
                return JsonResponse({
                    'reply': ai_response
                })
                
        except Exception as e:
            # Handle any errors that occur while processing the API response
            print(f"Error processing response: {e}")
            return JsonResponse({
                'error': f"Error processing response: {str(e)}",
                'detail': "The API returned a successful response, but there was an error processing it."
            }, status=500)
            
    except Exception as e:
        # Catch-all exception handler for any unhandled errors
        print(f"Error in ai_message_view: {str(e)}")
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
    Applies the AI-suggested changes to the site configuration by:
    1. Writing the new configuration to site_config.md
    2. Running the update_site_config management command to sync the file to the database
    
    Endpoint: /apply_changes/
    Method: POST
    Request Format:
        {
            "config": "Complete updated configuration file content"
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
        new_config = data.get('config', '')
        
        # Ensure we have a configuration to apply
        if not new_config:
            return JsonResponse({
                'error': 'No configuration provided',
                'detail': 'The request must include a complete configuration file.'
            }, status=400)
        
        # Step 2: Validate the configuration format
        if not new_config.startswith("# Site Configuration"):
            print("WARNING: Configuration doesn't start with expected header")
            return JsonResponse({
                'error': 'Invalid configuration format',
                'detail': 'The configuration must start with "# Site Configuration Template"'
            }, status=400)
            
        # Step 3: Save the new configuration to the site_config.md file
        config_path = os.path.join(settings.BASE_DIR, 'site_config.md')
        print(f"Writing new configuration to {config_path}")
        
        try:
            with open(config_path, 'w') as f:
                f.write(new_config)
            print(f"Successfully wrote {len(new_config)} characters to configuration file")
        except IOError as e:
            print(f"Error writing to configuration file: {str(e)}")
            return JsonResponse({
                'error': f"Error writing configuration file: {str(e)}",
                'detail': "Failed to save the new configuration to disk."
            }, status=500)
            
        # Step 4: Update the database from the file using the management command
        try:
            print("Running update_site_config management command...")
            call_command('update_site_config')
            print("Configuration successfully updated in database")
        except Exception as e:
            print(f"Error updating database from configuration file: {str(e)}")
            return JsonResponse({
                'error': f"Error updating database: {str(e)}",
                'detail': "The configuration file was saved but couldn't be synced to the database."
            }, status=500)
        
        # Step 5: Return success response
        return JsonResponse({
            'success': True, 
            'message': 'Configuration updated successfully in both file and database.'
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
        return JsonResponse({
            'error': f"Error applying changes: {str(e)}",
            'detail': "An unexpected error occurred while updating the configuration."
        }, status=500)