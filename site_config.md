# Site Configuration Template

This markdown file allows you to easily customize the content, style, and configuration of your MickBlog site. Edit the sections below and migrate the database to apply changes.

## Site Information

```yaml
brand: TVB
footer_text: "© 2025 Mick Darling. All rights reserved."
meta_description: Personal blog and portfolio site showcasing blog posts, projects, resume, and contact information.
tagline: Mick Darling's Projects, Posts, Resume, and Contact Info
title: TheVibeBlog

```

## Colors and Styling

```yaml
primary_color: '#6495ed'
secondary_color: '#add8e6'

```

## Custom CSS

Add any custom CSS below. This will be applied to the entire site.

```css
/* Custom CSS styles */
```

## About Me

Write your about information in markdown format below.

```markdown
This is my customized Blog project The Vibe Blog.  

It is one, among many other projects, that I will populate the Projects section with. 

I built this VibeCoding with ClaudeCode and added an easy to use AI interface on top of a Django platform so I can easily update the site dynamically with natural language, and I don't have to remember any workflow beyond asking the site to do something.
```
"
## Contact Information

```yaml
address: ''
email: mick@mickdarling.com
phone: ''

```

## Social Media

```yaml
bluesky_url: https://bsky.app/profile/mickdarling.bsky.social
facebook_url: https://facebook.com/mickdarling
github_url: https://github.com/mickdarling
instagram_url: https://instagram.com/mickdarling
linkedin_url: https://linkedin.com/in/mickdarling

```

## Google Analytics

```yaml
google_analytics_id: UA-XXXXXXXXX-X

```

## AI Configuration

```yaml
anthropic_api_key: # API key removed for security

```

---

## How to Apply Changes

After updating this file, run the following management command to apply the changes to your site:

```bash
python manage.py update_site_config
```

This will parse the markdown file and update the database with the new configuration.