# MickBlog - Personal Blog and Portfolio Site

A Django-based personal website with blog, projects portfolio, resume, and contact sections. Easy to customize with markdown templates.

## Features

- **Blog** - Post articles in markdown format with categories
- **Projects** - Showcase your portfolio with detailed project pages
- **Resume** - Display your education, experience, skills, and certifications
- **Contact** - Contact form with security features
- **Easy Customization** - Update content and styling through markdown templates
- **AI-Powered Configuration** - Use the integrated AI assistant to edit site configuration
- **Version History** - Track and restore previous configurations with detailed comparison views

## Installation

### Standard Installation

1. Clone the repository
```bash
git clone https://github.com/mickdarling/MickBlog.git
cd MickBlog
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Apply migrations
```bash
python manage.py migrate
```

4. Create a superuser
```bash
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

6. Apply site configuration from the template
```bash
python manage.py update_site_config
```

### Docker Installation (Recommended for Production)

1. Clone the repository
```bash
git clone https://github.com/mickdarling/MickBlog.git
cd MickBlog
```

2. Create and configure the environment file
```bash
cp .env.docker .env.docker.local
# Edit .env.docker.local with your secure passwords and settings
```

3. Build and start the Docker containers
```bash
docker-compose up -d --build
```

4. The application will be available at:
   - http://localhost (redirects to HTTPS)
   - https://localhost (secure access)

5. Access the admin interface at https://localhost/admin with the credentials specified in your .env.docker.local file.

## Customization

### Site Configuration

You have two ways to customize your site:

#### 1. Manual Editing

Edit the `site_config.md` file directly to customize:

- Site information (title, tagline, etc.)
- Colors and styling
- About content
- Contact information
- Social media links

After editing, run:
```bash
python manage.py update_site_config
```

With Docker, the site_config.md file is mounted as a volume, so changes are automatically applied without rebuilding the container.

#### 2. AI-Powered Editor (Recommended)

Use the integrated AI assistant to edit your site configuration:

1. Log in to the admin panel
2. Go to Site Configuration
3. Click the "AI Editor" button
4. Describe the changes you want in natural language
5. Review and apply the suggested changes

The AI assistant can help with tasks like:
- Updating site colors and styling
- Changing personal information
- Editing about page content
- Adding social media links
- Customizing CSS

To use this feature, you need an Anthropic API key. You have two options:

**Option 1: Environment Variable** (recommended for development)
1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Add it to your `.env` file as `ANTHROPIC_API_KEY=your_key_here`

**Option 2: Site Configuration** (recommended for production)
1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Add it to the "Anthropic API key" field in the Site Configuration admin 

For detailed instructions on using the AI editor, see [AI_EDITOR_USAGE.md](AI_EDITOR_USAGE.md)

### Custom Styling

Add custom CSS in the "Custom CSS" section of `site_config.md` or use the AI assistant to generate and apply CSS changes.

### Content Management

Access the admin panel at `/admin` to manage:

- Blog posts and categories
- Projects and technologies
- Resume sections (education, experience, skills, certifications)
- Site configuration
- Configuration version history

### Version History

The site configuration includes complete version history functionality:

1. Every change to the site configuration is automatically tracked
2. View the history of changes with user information and timestamps
3. Compare versions with detailed side-by-side field comparison
4. Recover previous versions with a single click
5. Automatic handling of complex fields like custom CSS during recovery

## Security Features

The site includes several security features:

- Environment-based configuration
- CSRF protection
- XSS protection
- Content security policy headers
- HTTPS enforcement (in production)
- HSTS headers (in production)
- IP logging for contact form submissions

## Docker Deployment Details

The Docker setup includes:

- **Web Application Container**: Django + Gunicorn
- **Database Container**: PostgreSQL
- **Web Server Container**: Nginx with SSL

Persistent volumes are used for:
- Database data
- Media uploads
- Static files
- Site configuration

## Manual Deployment

For manual production deployment:

1. Set `DEBUG=False` in the `.env` file
2. Configure a proper database (PostgreSQL recommended)
3. Set up static and media files serving
4. Configure a proper mail backend
5. Set a strong SECRET_KEY
6. Configure ALLOWED_HOSTS

## Credits

Created with:

- Django
- Bootstrap 5
- Markdownx
- Font Awesome
- Docker
- Nginx
- PostgreSQL
- Gunicorn
- Claude AI (for AI-powered configuration editor)