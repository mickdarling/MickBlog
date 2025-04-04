# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Commands
- Development: `python manage.py runserver`, `python manage.py runhttps`, `python manage.py migrate`, `python manage.py collectstatic`, `python manage.py export_site_config`, `python manage.py update_site_config`
- Testing: `python manage.py test app_name.tests.TestClassName.test_method_name` (for single test), `python manage.py test app_name` (for all app tests)
- Version history testing: `python manage.py test_version_history`, `./test_versions.sh`
- Docker: `docker-compose up -d`, `docker-compose logs -f web`, `docker-compose build`

## Common Issues & Solutions
- **API Keys**: Store in `.env` file, never commit to repo. If AI editor errors with 500, check API key configuration
- **Version History**: If recovery fails, verify field mapping in admin_site.py recover_view
- **Configuration**: If site changes aren't reflected, run update_site_config command
- **Blog Content**: Posts must have "published" status to be visible
- **AI Blog Editor**: If content doesn't appear in editor, check regex patterns in blog/views.py (ai_blog_conversation_view)
- **AI Response Parsing**: Look for structured format with ```conversation and ```blogpost sections

## Code Style & Project Direction
- Follow PEP 8, Django naming conventions (snake_case for variables/functions, CamelCase for classes)
- Class-based views preferred, with comprehensive docstrings following Google style
- Order imports: standard library → Django → third-party → local apps
- Django 5.1+ project with modular apps (blog, projects, resume, contact, core)
- Use f-strings for string formatting (Python 3.6+ project)
- Error handling: use try/except with specific exceptions, never pass silently
- Use django-reversion for version history tracking with proper revision comments
- Tests follow AAA pattern (Arrange, Act, Assert)
- Backup files (with .bak extension) must be maintained for all source files
- Current priorities: AI integration, content management - see TODO.md for details

## Project Structure
- Django 5.1+ with Bootstrap 5 frontend
- Uses markdownx for content editing with markdown
- PostgreSQL in production (via Docker), SQLite in development
- Nginx for production serving with HTTPS
- Environment variables via django-environ
- Version control via django-reversion 
- AI integration via Anthropic Claude API
- Two complementary AI blog content creation tools:
  1. **AI Blog Editor (Conversational)**: Two-panel interface with chat and editor
  2. **AI-AutoCreate (Form-based)**: Structured form for guided content generation

## AI Response Structure
When working with the AI blog content creation tools, responses are structured with specific markers:

```
```conversation
This is the conversational part that appears in the chat panel
```

```blogpost
This is the blog content that appears in the editor panel
```
```

This structure allows for clean separation of conversation from content.

For detailed documentation on architecture, troubleshooting, and known issues, see [REFERENCE.md](./REFERENCE.md)