# Site Configuration Template

This markdown file allows you to easily customize the content, style, and configuration of your MickBlog site. Edit the sections below and migrate the database to apply changes.

## Site Information

```yaml
brand: MB
footer_text: "© 2025 Your Name. All rights reserved."
meta_description: Personal blog and portfolio site showcasing blog posts, projects,
  resume, and contact information.
tagline: Projects, Posts, Resume, and Contact Info
title: Your Personal Blog

```

## Colors and Styling

```yaml
primary_color: '#007bff'
secondary_color: '#6c757d'

```

## Custom CSS

Add any custom CSS below. This will be applied to the entire site.

```css
/* Custom Bluesky icon styling */
.bluesky-icon {
  color: #1185fe;  /* Bluesky's brand color */
  font-size: 1.1em;
}

/* Make the nav icons a bit larger for better visibility */
.navbar-nav .nav-link i {
  font-size: 1.2em;
}
```

## About Me

Write your about information in markdown format below.

```markdown
I am a software developer with experience in web development, machine learning, and data analysis. This is my personal blog and portfolio site.
```

## Contact Information

```yaml
address: ''
email: your.email@example.com
phone: ''

```

## Social Media

```yaml
bluesky_url: https://bsky.app/profile/yourusername.bsky.social
facebook_url: https://facebook.com/yourusername
github_url: https://github.com/yourusername
instagram_url: https://instagram.com/yourusername
linkedin_url: https://linkedin.com/in/yourusername

```

## Google Analytics

```yaml
google_analytics_id: UA-XXXXXXXXX-X

```

---

## How to Apply Changes

After updating this file, run the following management command to apply the changes to your site:

```bash
python manage.py update_site_config
```

This will parse the markdown file and update the database with the new configuration.