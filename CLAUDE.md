# MickBlog Project Context

## Project Overview
MickBlog is a Django-based personal website/blog with AI-powered site configuration capabilities. The project allows for both traditional database configuration and natural language editing through Claude AI integration.

## Key Features
- Django admin customization with AI-powered editor
- Anthropic Claude API integration for natural language site configuration
- Bidirectional synchronization between database and markdown files
- Docker containerization for development and deployment

## Recent Changes & Fixes
- Improved AI Editor UX with single editable configuration field
  - Replaced tabbed Current/Suggested Config with unified editor
  - Added Apply/Undo Changes buttons
  - Fixed bugs in buttons event handling
- Fixed regex pattern for About Me section parsing
  - Enhanced markdown block extraction for greater flexibility
  - Improved debug logging for configuration parsing
- Fixed blog post publishing workflow
  - Posts need "published" status to be visible
- Enhanced CSS for responsive design
  - Constrained editor height to prevent overflow
  - Added proper scrollbars in content areas
  - Fixed sizing issues on various screen sizes

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
- Docker restart: `docker-compose restart`
- Collect static files: `python manage.py collectstatic --noinput`

## Configuration
- Anthropic API key can be set via:
  1. Environment variable: ANTHROPIC_API_KEY
  2. Database: SiteConfig model's anthropic_api_key field (requires 83+ characters)
  
## AI Editor Architecture
- **Two-Step API Flow**: 
  - First API call for conversational chat response
  - Second API call for site configuration generation
- **URL Endpoints**:
  - `/ai_message/` - Handles conversational responses
  - `/ai_config/` - Generates configuration file updates
  - `/apply_changes/` - Applies suggested changes to site_config.md and database
  - `/test_json/` - Simple test endpoint for debugging
- **UI Components**:
  - Left panel: Conversation with AI
  - Right panel: Unified Configuration Editor
  - Apply Changes button to commit changes
  - Undo Changes button to revert to original config
  - Generate Config button for direct config generation

## Troubleshooting
- If blog posts are not visible, check if their status is set to "published"
- If site configuration changes aren't reflected, run `update_site_config` command
- If About Me section isn't updating, ensure the markdown block format in site_config.md is correct
- For JavaScript issues, check browser console for errors and ensure collectstatic has run

## Coding Style
- PEP 8 for Python code
- Django naming conventions
- Class-based views preferred over function-based views
- Comprehensive docstrings for all significant functions/methods
- CSS using flexbox for responsive design
- JavaScript: vanilla JS preferred (no jQuery dependencies) for better compatibility

## Technologies
- Django 5.1
- PostgreSQL (production) / SQLite (development)
- Docker & Docker Compose
- Anthropic Claude API (Claude 3 Sonnet)
- NGINX (production)
- Markdown/YAML for configuration
- Vanilla JavaScript