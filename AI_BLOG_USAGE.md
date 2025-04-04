# MickBlog AI Blog Content Creation Guide

MickBlog offers two powerful AI-powered tools for creating and refining blog content. This guide explains both tools and how to use them effectively.

## Setup

Before using the AI Blog tools, you need an Anthropic API key. You have two options for setting it up:

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

Both tools will use the API key from either source, with the environment variable taking precedence if both are set.

## Tool 1: AI Blog Editor (Conversational)

A conversational interface that allows you to create and refine blog content through natural language dialogue.

### Accessing the AI Blog Editor

1. Log in to the Django admin interface (`/admin`)
2. Navigate to "Blog" > "Posts"
3. Click the "AI Blog Editor" button in the upper right corner

### Using the AI Blog Editor

The AI Blog Editor interface has two main sections:

#### Left Side: Chat Interface

This is where you communicate with the AI assistant. You can:

- Describe the blog post you want to create in natural language
- Ask for improvements or changes to existing content
- Discuss ideas and get suggestions
- Request edits to specific sections

#### Right Side: Blog Editor

This shows:
- The current blog post content
- Markdown formatting
- Preview toggle for rendered content
- Diff view for comparing changes

#### Example Interactions

Here are some examples of how to use the AI Blog Editor:

##### Creating a New Post

```
Please create a blog post about the benefits of using Django for web development. Focus on how Django's batteries-included approach saves time for developers.
```

##### Improving Existing Content

```
Can you improve this introduction to make it more engaging? I want to hook readers right from the start.
```

##### Requesting Specific Changes

```
Please add a section about Django's security features and how they protect against common web vulnerabilities.
```

##### Comparing Versions

After the AI suggests changes, you can:
1. Click "Show what changed" to see a side-by-side comparison
2. Review the differences with highlighted changes
3. Apply the changes or continue editing

##### Saving Your Post

When you're satisfied with the content:
1. Click "Save Post"
2. Choose a title, category, and publication status
3. The post will be saved to your blog database

## Tool 2: AI-AutoCreate (Form-based)

A structured form interface for guided blog post generation with specific parameters.

### Accessing AI-AutoCreate

1. Log in to the Django admin interface (`/admin`)
2. Navigate to "Blog" > "Posts"
3. Click the "AI-AutoCreate" button in the upper right corner

### Using AI-AutoCreate

The form has several fields to guide the AI's content generation:

1. **Title** (optional): Provide a title or leave blank for AI to generate one
2. **Topic**: The main subject of your blog post
3. **Tone**: Desired writing style (professional, conversational, academic, etc.)
4. **Length**: Approximate word count (brief, standard, detailed)
5. **Structure**: How the post should be organized (listicle, deep-dive, how-to, etc.)
6. **Target Audience**: Who the post is intended for (beginners, experts, etc.)
7. **Key Points** (optional): Specific points you want to include
8. **SEO Keywords** (optional): Terms to incorporate for search optimization

Click "Generate Post" and the AI will create content based on your parameters. You can then:

1. Preview the generated content
2. Edit it manually if needed
3. Save as draft or publish directly

## Best Practices

- Be specific about what you want when describing post ideas
- Use the conversational editor for iterative refinement
- Use AI-AutoCreate when you need quick content with specific parameters
- Always review AI-generated content before publishing
- For complex topics, provide some key information or resources for the AI
- Save frequently during long editing sessions
- Use the preview toggle to check how markdown will render

## Troubleshooting

- **Error connecting to AI**: Verify your API key is correct in the .env file
- **Content doesn't update**: Check for JavaScript errors in your browser console
- **Markdown not rendering**: Ensure proper markdown syntax is being used
- **Changes revert unexpectedly**: Make sure to apply changes before switching to preview mode
- **Diff view not working**: Verify both original and new content are available

---

These AI tools are designed to help you create high-quality blog content more efficiently. They handle the heavy lifting of content generation while giving you full control over the final output.