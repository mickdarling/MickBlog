# MickBlog Project Context

## Project Overview
MickBlog is a Django-based personal website/blog with AI-powered site configuration capabilities. The project allows for both traditional database configuration and natural language editing through Claude AI integration.

## Key Features
- Django admin customization with AI-powered editor
- Anthropic Claude API integration for natural language site configuration
- Bidirectional synchronization between database and markdown files
- Docker containerization for development and deployment
- Version history tracking with comparison and recovery
- Robust error handling and API key management

## Recent Changes & Fixes

### April 2025 Updates

#### Fixed Version History and AI Editor Functionality
- Fixed django-reversion integration for complete version history
- Added comprehensive version comparison UI with styled templates
- Implemented field-by-field version recovery with proper database updates
- Fixed custom CSS handling during version recovery
- Created test scripts to verify version history functionality
- Added detailed history and recovery confirmation templates

#### Combined AI Endpoint for Better Reliability
- Implemented a single endpoint for both natural language and configuration responses
- Created structured AI prompting system with clear section markers
- Added robust regex-based parsing for AI responses
- Implemented special handling for "no changes needed" cases
- Enhanced error handling with comprehensive logging

#### Improved API Key Management
- Created robust API key handling with multiple fallbacks:
  1. Django settings (in-memory)
  2. Environment variables
  3. Reloading from .env file
  4. Direct reading from .env as last resort
- Added proper error handling for missing or invalid API keys
- Implemented API key masking in the UI (showing only first/last 5 chars)
- Added user-friendly API key setup form with validation

#### Enhanced Code Quality and Documentation
- Added comprehensive documentation to key functions
- Improved code comments for better maintainability
- Created repository information file with proper author attribution
- Updated README with version history features
- Removed any sensitive data from repository history

### Previous Updates
- Improved API key security and handling:
  - Added environment variable support via `.env` file
  - Updated model to allow NULL values for API key
  - Added clear instructions for API key management
- Fixed container startup issues:
  - Resolved NOT NULL constraint error with API key
  - Added migration to allow NULL values in anthropic_api_key field
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

### Development
- Start development server: `python manage.py runserver`
- Start HTTPS development server: `python manage.py runhttps`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Export site config: `python manage.py export_site_config`
- Update site config: `python manage.py update_site_config`
- Collect static files: `python manage.py collectstatic --noinput`

### Testing
- Test version history: `python manage.py test_version_history`
- Run test script: `./test_versions.sh`

### Docker
- Docker development: `docker-compose up -d`
- Docker restart: `docker-compose restart`
- Docker rebuild: `docker-compose down && docker-compose up -d`
- Docker logs: `docker-compose logs -f web`

## Configuration
- Anthropic API key can be set via:
  1. Environment variable: ANTHROPIC_API_KEY (preferred method)
     - Set in `.env` file at project root
     - Automatically picked up by docker-compose and Django settings
  2. Database: SiteConfig model's anthropic_api_key field
     - Set in Django admin > Site Configuration
     - Only used if environment variable isn't set

## API Key Security
- NEVER commit API keys to Git repositories
- The `.env` file is in `.gitignore` to prevent accidental commits
- API keys in site_config.md are masked (e.g., "sk-an...p0gAA")
- Use environment variables in production environments
- When viewing the site_config.md file, API keys are shown with a security note
- API keys in Django admin are never exported in full form to markdown files

## Docker Setup
- Set environment variables in `.env` file
- Docker reads variables from host environment or `.env` file
- Development container uses a volume mount to enable live code editing
- Container runs migrations and site_config updates on startup
  
## AI Editor Architecture
- **Combined Endpoint Flow**: 
  - Single API call to `/ai_config/` for both chat response and configuration
  - Structured response format with explicit section markers
  - Multiple fallbacks for various response types
- **URL Endpoints**:
  - `/ai_config/` - Handles both conversational responses and configuration generation
  - `/apply_changes/` - Applies suggested changes to site_config.md and database
  - `/test_json/` - Simple test endpoint for debugging
  - `/admin/api-key-setup/` - UI for API key configuration
  - `/admin/config-history/` - Version history browsing interface
- **UI Components**:
  - Left panel: Conversation with AI
  - Right panel: Unified Configuration Editor
  - Apply Changes button to commit changes
  - Undo Changes button to revert to original config
  - Generate Config button for direct config generation

## Troubleshooting

### Version History Issues
- If version history comparison shows incorrect data, check the field comparison logic in admin_site.py
- If version recovery fails, verify proper field mapping in the recover_view method
- If custom CSS isn't correctly restored after recovery, check the CSS handling in SiteConfig.save()
- Run the test script with `python manage.py test_version_history` to verify version history functionality

### AI Editor Issues
- If AI editor returns 500 error, check if API key is properly configured and formatted correctly
- For "No changes needed" responses, verify the structured output parsing and json_match regex
- If changes aren't applied correctly, check the apply_changes_view function for field mapping
- For JavaScript errors, check browser console and network tab for failed requests

### General Issues
- If blog posts are not visible, check if their status is set to "published"
- If site configuration changes aren't reflected, run `update_site_config` command
- If About Me section isn't updating, ensure the markdown block format in site_config.md is correct
- For JavaScript issues, check browser console for errors and ensure collectstatic has run
- If container keeps restarting, check logs with `docker logs mickblog_dev`
- API key issues: use the robust get_anthropic_api_key function for debugging

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
- Environment variables via django-environ