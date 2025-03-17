# MickBlog AI Editor Usage Guide

The AI Editor is a powerful tool that allows you to modify your site configuration using natural language instructions. This guide explains how to set it up and use it effectively.

## Setup

Before using the AI Editor, you need an Anthropic API key. You have two options for setting it up:

### Option 1: Environment Variable (recommended for development)

1. Go to [Anthropic Console](https://console.anthropic.com/) and create an account if you don't have one
2. Generate an API key from your account settings
3. Add the API key to your `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Restart your Django server or Docker container

### Option 2: Site Configuration (recommended for production)

1. Go to [Anthropic Console](https://console.anthropic.com/) and create an account if you don't have one
2. Generate an API key from your account settings
3. Log in to the Django admin interface
4. Navigate to "Core" > "Site Configuration"
5. Open the existing configuration
6. Expand the "AI Configuration" section
7. Enter your API key in the "Anthropic API key" field
8. Save the configuration

The editor will use the API key from either source, with the environment variable taking precedence if both are set.

## Accessing the AI Editor

1. Log in to the Django admin interface (`/admin`)
2. Navigate to "Core" > "Site Configuration"
3. Click on the existing site configuration
4. Click the "AI Editor" button in the upper right corner

## Using the AI Editor

The AI Editor interface has two main sections:

### Left Side: Chat Interface

This is where you communicate with the AI assistant. You can:

- Ask questions about your current configuration
- Request specific changes
- Get recommendations for improvements

### Right Side: Configuration Editor

This shows:
- **Current Config**: Your existing site configuration
- **Suggested Changes**: Changes proposed by the AI assistant

## Example Interactions

Here are some examples of how to use the AI Editor:

### Changing Basic Information

```
Please update the site title to "John's Tech Blog" and the tagline to "Exploring Software Development and AI"
```

### Updating Colors

```
I'd like to change my site's color scheme to use a dark blue primary color and a light gray secondary color
```

### Editing About Text

```
Please rewrite my about section to be more professional and mention my experience with Python, Django, and machine learning
```

### Adding Social Media Links

```
Add these social media links:
- GitHub: https://github.com/johndoe
- LinkedIn: https://linkedin.com/in/johndoe
- Twitter: https://twitter.com/johndoe
```

### Customizing CSS

```
Can you add some CSS to make the navbar links have a transition effect when hovered over? Also add a subtle shadow to all cards on the site.
```

## Applying Changes

After the AI suggests changes:

1. Review the suggested configuration in the right panel
2. If everything looks good, click "Apply Changes"
3. If you want to modify the suggestion, continue the conversation with the AI
4. If you prefer to apply the changes manually, click "Copy to Clipboard" and update your site_config.md file directly

## Best Practices

- Be specific about what you want to change
- Review AI suggestions carefully before applying them
- Use the AI for inspiration, but feel free to modify its suggestions
- Remember that the AI can only modify configuration, not actual code
- For complex CSS changes, consider providing examples of what you want

## Troubleshooting

- **Error connecting to AI**: Verify your API key is correct in the .env file
- **Changes not applying**: Make sure your file permissions allow writing to site_config.md
- **CSS not updating**: Remember to refresh your browser with cache clearing (Ctrl+F5)

---

The AI Editor provides a natural language interface to your site's configuration, making it easier than ever to customize your site without directly editing files or learning YAML syntax.