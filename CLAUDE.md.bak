# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Commands
- Development: `python manage.py runserver`, `python manage.py runhttps`, `python manage.py migrate`
- Testing: `python manage.py test app_name.tests.TestClassName.test_method_name` (single test)
- Config: `python manage.py export_site_config`, `python manage.py update_site_config`
- Docker: `docker-compose up -d`, `docker-compose build`

## Code Style
- PEP 8 with Django naming conventions (snake_case for variables/functions, CamelCase for classes)
- Order imports: standard library → Django → third-party → local apps
- Use f-strings, Google-style docstrings, specific exception handling
- Maintain .bak files for all source files when editing
- Prefer class-based views; follow AAA pattern for tests (Arrange, Act, Assert)

## Project Structure
- Django 5.1+ with Bootstrap 5 frontend, PostgreSQL/SQLite databases
- Core apps: blog, contact, core, projects, resume
- AI features: Content editor with version history, form-based content generator
- Blog Editor: Persistent drafts, side-by-side editing, synchronized scrolling
- AI Response Format: Use structured sections (```conversation and ```blogpost)
- Content: Smart handling for long documents with focused editing options

For detailed documentation see [REFERENCE.md](./REFERENCE.md) and [TODO.md](./TODO.md)