# MickBlog Project Context

## Project Overview
MickBlog is a Django-based personal website/blog with AI-powered site configuration capabilities. The project allows for both traditional database configuration and natural language editing through Claude AI integration.

## Key Features
- Django admin customization with AI-powered editor
- Anthropic Claude API integration for natural language site configuration
- Bidirectional synchronization between database and markdown files
- Docker containerization for development and deployment

## Recent Changes
Recently added an AI-powered editor for site configuration that allows users to:
- Edit site settings using natural language
- Preview changes before applying them
- Bidirectionally sync between database and markdown files

Recent fixes (March 2025):
- Completely overhauled Anthropic API integration for reliable communication
- Implemented comprehensive error handling with detailed logging and structured responses
- Optimized system prompts for better configuration generation results
- Fixed authentication with proper Bearer token and x-api-key formats
- Updated API request format to match latest Anthropic specifications
- Added extensive documentation for all API endpoints with step-by-step approach
- Removed debugging alerts and improved JavaScript error handling
- Added configuration validation before applying changes
- Fixed relative URL paths to use absolute paths throughout
- Implemented consistent error message format for better UX
- Enhanced logging throughout to facilitate easier debugging

## Project Structure
- Core Django apps: blog, contact, core, projects, resume
- Custom admin interface in core/admin
- AI editor implementation in core/admin/views.py and templates
- Static assets for AI editor in core/static/core/

## Common Commands
- Start development server: `python manage.py runserver`
- Start HTTPS development server: `python manage.py runhttps`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Export site config: `python manage.py export_site_config`
- Update site config: `python manage.py update_site_config`
- Docker development: `docker-compose up`

## Configuration
- Anthropic API key can be set via:
  1. Environment variable: ANTHROPIC_API_KEY
  2. Database: SiteConfig model's anthropic_api_key field (requires 83+ characters)
  
## AI Editor Troubleshooting
- The field for Anthropic API key must be 255 chars long (migration 0004_increase_api_key_length fixes this)
- Anthropic API requires system messages as a top-level parameter in the request body
- Current API format uses:
  - Headers:
    - "Content-Type": "application/json"
    - "Authorization": "Bearer {api_key}"
    - "x-api-key": "{api_key}" (for backward compatibility)
    - "anthropic-version": "2023-06-01"
  - Request body:
    - "model": "claude-3-sonnet-20240229"
    - "max_tokens": 4000
    - "temperature": 0.3 (for config generation) or 0.7 (for conversation)
    - "messages": array of role/content objects
    - "system": string containing system instructions

## API Endpoints
- `/ai_message/`: Conversational endpoint that returns helpful explanations
  - Request: `{"message": "user question", "history": [previous messages]}`
  - Response: `{"reply": "assistant response"}`
- `/ai_config/`: Configuration generation endpoint that returns full config files
  - Request: `{"message": "change request"}`
  - Response: `{"config": "complete config file"}`
- `/apply_changes/`: Endpoint to apply configuration changes
  - Request: `{"config": "complete config file"}`
  - Response: `{"success": true, "message": "success message"}`

## AI Editor Architecture
- **Two-Step API Flow**: 
  - First API call for conversational chat response
  - Second API call for site configuration generation
- **URL Endpoints**:
  - `/ai_message/` - Handles conversational responses
  - `/ai_config/` - Generates configuration file updates
  - `/apply_changes/` - Applies suggested changes to site_config.md and database
  - `/test_json/` - Simple test endpoint for debugging
- **Mock Implementations**:
  - `mock_ai_config_view` - Rule-based configuration generator (no API needed)
  - `mock_apply_changes_view` - Simplified version for testing
- **UI Components**:
  - Left panel: Conversation with AI
  - Right panel: Current and Suggested Configurations
  - Apply Changes button to commit changes
  - Generate Config button for direct config generation

## Coding Style
- PEP 8 for Python code
- Django naming conventions
- Class-based views preferred over function-based views
- Comprehensive docstrings for all significant functions/methods
- CSS using flexbox for responsive design
- JavaScript: vanilla JS preferred (no jQuery dependencies) for better compatibility

## Technologies
- Django
- PostgreSQL (production) / SQLite (development)
- Docker & Docker Compose
- Anthropic Claude API (Claude 3 Sonnet)
- NGINX (production)
- Markdown/YAML for configuration
- Vanilla JavaScript (no jQuery dependencies)