from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
import re
import requests
import traceback
from markdownx.utils import markdownify
from difflib import SequenceMatcher
from .models import Post, Category
from .forms import AIPostGeneratorForm
from core.models import SiteConfig
from core.utils import get_anthropic_api_key

def post_list(request, slug=None):
    """
    View for listing blog posts, optionally filtered by category.
    
    This view handles both the main blog listing and category-specific listings.
    It includes pagination, sidebar widgets for categories and recent posts,
    and passes the site configuration for consistent styling.
    
    Args:
        request: The HTTP request
        slug: Optional category slug to filter posts by
        
    Returns:
        Rendered template with paginated posts and sidebar widgets
    """
    # Get site configuration (legacy approach - middleware now provides this via request.site_config)
    # We keep this for backwards compatibility and to ensure the site variable is always available
    site = SiteConfig.get()
    
    # Initialize category for template context
    category = None
    
    # Get published posts, optionally filtered by category
    if slug:
        # Category-specific listing
        category = get_object_or_404(Category, slug=slug)
        posts_list = Post.objects.filter(status='published', category=category)
    else:
        # Main blog listing
        posts_list = Post.objects.filter(status='published')
    
    # Get recent posts for sidebar widget - limited to 5 most recent
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:5]
    
    # Get all categories for sidebar widget
    categories = Category.objects.all()
    
    # Pagination - 5 posts per page
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page parameter is not an integer or missing, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    # Prepare template context
    context = {
        'posts': posts,
        'category': category,
        'categories': categories,
        'recent_posts': recent_posts,
        'site': site,
    }
    
    return render(request, 'blog/post_list.html', context)

def post_detail(request, year, month, day, slug):
    """
    View for displaying a specific blog post.
    
    This view shows a single post with its full content, identified by its
    publication date components and slug. It also provides navigation to
    previous and next posts for easy browsing through the blog.
    
    Args:
        request: The HTTP request
        year: Publication year (integer)
        month: Publication month (integer)
        day: Publication day (integer)
        slug: Post slug for URL-friendly title
        
    Returns:
        Rendered template with the post and navigation links
    """
    # Get site configuration
    site = SiteConfig.get()
    
    # Get the specific post with date and slug validation
    # This creates a user-friendly 404 if the post doesn't exist or isn't published
    post = get_object_or_404(Post,
                            slug=slug,
                            status='published',
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    
    # Get previous and next posts for navigation
    # This creates a chronological browsing experience through the blog
    prev_post = Post.objects.filter(status='published', publish__lt=post.publish).order_by('-publish').first()
    next_post = Post.objects.filter(status='published', publish__gt=post.publish).order_by('publish').first()
    
    # Prepare template context
    context = {
        'post': post,
        'prev_post': prev_post,
        'next_post': next_post,
        'site': site,
    }
    
    return render(request, 'blog/post_detail.html', context)

# Check if user is staff (for admin-only views)
def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def ai_blog_editor_view(request):
    """
    View for the AI blog editor interface.
    
    This view provides a conversational interface for creating and editing blog posts
    with AI assistance. Unlike the AI post generator, this interface allows for
    interactive refinement through natural language conversation.
    
    The AI Blog Editor features:
    - Two-panel interface with chat on the left and editor on the right
    - Structured AI responses with both conversation and blog content
    - Real-time content updates as the conversation progresses
    - Content improvement suggestions with diff view
    - Live preview of markdown formatting
    
    Args:
        request: The HTTP request
        
    Returns:
        Rendered template with the blog editor interface
    """
    # Check if API key is configured
    api_key = get_anthropic_api_key()
    api_key_configured = bool(api_key)
    
    # Get all categories for the dropdown
    categories = Category.objects.all()
    
    # Get staff users for the author dropdown
    authors = User.objects.filter(is_staff=True)
    
    context = {
        'api_key_configured': api_key_configured,
        'categories': categories,
        'authors': authors,
    }
    
    return render(request, 'blog/ai_blog_editor.html', context)

@csrf_exempt
@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def ai_blog_conversation_view(request):
    """
    API endpoint for the AI blog editor conversation.
    
    This view handles the back-and-forth conversation with the AI, taking the user's
    message and current blog state, and returning AI suggestions and content updates.
    
    The AI response is structured with two distinct sections:
    1. `conversation` - A natural language response to the user's message
    2. `blogpost` - The full blog post content in markdown format
    
    This structured approach allows the system to:
    - Maintain a natural conversation with the user
    - Automatically extract and update the blog content in the editor
    - Keep the full post context across multiple interactions
    
    Args:
        request: The HTTP request with JSON data containing:
            - message: The user's message
            - title: Current blog post title (optional)
            - content: Current blog post content (optional)
            - category: Current blog post category (optional)
        
    Returns:
        JsonResponse with:
            - reply: The AI's conversational response
            - content: The updated blog post content (if provided)
            - title: A suggested title (if provided)
            - overwrite_title: Whether to overwrite an existing title
    """
    # Get API key and verify it's configured
    api_key = get_anthropic_api_key()
    
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Parse the request body
        data = json.loads(request.body)
        message = data.get('message', '')
        title = data.get('title', '')
        content = data.get('content', '')
        category = data.get('category', '')
        
        # Validate message
        if not message:
            return JsonResponse({
                'error': 'Message is required',
                'detail': 'Please provide a message to continue the conversation.'
            }, status=400)
        
        # Determine if this is an initial request or a follow-up
        is_initial = not content
        
        # Craft system prompt based on whether this is initial or follow-up
        if is_initial:
            system_message = """You are a professional blog content creator who helps users write engaging blog posts.
Your goal is to assist the user in creating high-quality blog content through conversation.

EXTREMELY IMPORTANT: Format your responses in TWO distinct parts as follows:

```conversation
Your conversational response to the user goes here. Be friendly, helpful, and concise.
```

```blogpost
The full blog post content in markdown format goes here, including title and properly formatted content.
```

IMPORTANT GUIDELINES:
1. ALWAYS include both a conversation section AND a blogpost section in your response.
2. For the first interaction, immediately generate a complete blog post draft based on the user's topic.
3. Your conversation part should be friendly and briefly explain what you've created.
4. The blogpost part MUST start with a title as a level 1 heading (# Title) followed by the content.
5. Use proper markdown formatting with headings (##, ###), lists, emphasis, etc.
6. When updating the blog post, include the COMPLETE UPDATED POST, not just the changed sections.
7. Create approximately 600-800 words with:
   - A strong introduction
   - 2-3 well-developed body sections with appropriate headings
   - A concise conclusion
8. Ensure the content is informative, engaging and valuable to readers.
9. Never ask questions without providing a blog post draft.

This format allows the system to automatically extract the blog post content and update the editor while maintaining a natural conversation with the user.
"""
        else:
            system_message = """You are a professional blog content editor who helps users refine their blog posts.
Your goal is to assist the user in improving their existing blog content through conversation.

EXTREMELY IMPORTANT: Format your responses in TWO distinct parts as follows:

```conversation
Your conversational response to the user goes here. Be friendly, helpful, and concise.
Briefly explain the changes you've made to the blog post.
```

```blogpost
The COMPLETE UPDATED blog post content in markdown format, with all changes applied.
Always include the full post, starting with the title as a level 1 heading.
```

IMPORTANT GUIDELINES:
1. ALWAYS include both a conversation section AND a blogpost section in your response.
2. Your conversation part should explain what changes you've made and why.
3. The blogpost part MUST be the COMPLETE updated post (not just the changes).
4. The blogpost MUST start with a title as a level 1 heading (# Title).
5. Use proper markdown formatting with headings (##, ###), lists, emphasis, etc.
6. Make the specific changes the user requested.
7. Keep the user's style and voice consistent.
8. Respect the user's creative direction while offering expert guidance.
9. Never provide just a conversational response without the updated blog post.

The user's existing blog post is provided. Reference specific sections when discussing your changes.
Your blogpost section will completely replace the current content in the editor.
"""

        # Craft user prompt
        if is_initial:
            user_prompt = f"""I'd like your help creating a blog post about: {message}

{f"The category is: {category}" if category else ""}
{f"The title might be: {title}" if title else ""}

Please help me develop this idea into a well-structured blog post. You can ask clarifying questions or suggest a draft to get started."""
        else:
            user_prompt = f"""Current blog post title: {title or "Untitled"}
{f"Category: {category}" if category else ""}

Current content:
```
{content}
```

My request: {message}

Please help with this specific request about the blog post. If you suggest substantial edits, please explain your reasoning."""

        # Prepare API request
        clean_api_key = api_key.strip().strip('"\'')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_api_key}",
            "anthropic-version": "2023-06-01",
            "x-api-key": clean_api_key
        }
        
        # Configure API request with optimized parameters
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,  # Set to maximum allowed for this model to handle longer responses
            "temperature": 0.7,  # Balanced creativity vs determinism
            "messages": [{"role": "user", "content": user_prompt}],
            "system": system_message
        }
        
        # Make the API request with extended timeout for large documents
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=request_body,
            timeout=180  # Increased timeout to 3 minutes to accommodate larger responses
        )
        
        # Handle API response errors
        if response.status_code != 200:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                    else:
                        error_message = str(error_data['error'])
            except Exception:
                error_message = f"API error: {response.status_code}"
                
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'status_code': response.status_code,
                'detail': "The Anthropic API returned an error. Please check the API key and try again."
            }, status=500)
        
        # Process the successful response
        response_data = response.json()
        ai_response = response_data['content'][0]['text']
        
        # Extract conversation and blogpost parts
        conversation_match = re.search(r'```conversation\s*([\s\S]*?)\s*```', ai_response)
        blogpost_match = re.search(r'```blogpost\s*([\s\S]*?)\s*```', ai_response)
        
        # Extract the conversation part (for the chat)
        conversation_part = conversation_match.group(1).strip() if conversation_match else ai_response
        
        # Extract the blogpost part (for the editor)
        blogpost_content = blogpost_match.group(1).strip() if blogpost_match else None
        
        # Extract the title from the blogpost content
        title_match = re.search(r'^\s*#\s+([^\n]+)', blogpost_content) if blogpost_content else None
        suggested_title = title_match.group(1).strip() if title_match else None
        
        # For debugging
        print(f"Extracted conversation: {conversation_part[:100]}...")
        print(f"Extracted blogpost: {blogpost_content[:100] if blogpost_content else 'None'}...")
        print(f"Extracted title: {suggested_title or 'None'}")
        
        # Prepare response data
        result = {
            'reply': conversation_part,
        }
        
        # Add content and title if available
        if blogpost_content:
            result['content'] = blogpost_content
        
        if suggested_title:
            result['title'] = suggested_title
            result['overwrite_title'] = not title  # Only overwrite if no title was provided
        
        return JsonResponse(result)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'detail': 'The request must include a valid JSON object.'
        }, status=400)
    except Exception as e:
        print(f"Error in ai_blog_conversation_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error: {str(e)}",
            'detail': "An unexpected error occurred during the conversation."
        }, status=500)

@csrf_exempt
@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def ai_blog_improve_view(request):
    """
    API endpoint for improving blog content.
    
    This view sends the current blog content to the AI for analysis and suggestions.
    The AI returns both specific improvement suggestions and a complete improved
    version of the content that can be previewed, compared, or applied.
    
    The improvement workflow offers multiple user interactions:
    1. Preview - Toggle between original and improved versions
    2. Diff View - Side-by-side comparison with highlighted changes
    3. Apply - Update the editor with the improved content
    
    Args:
        request: The HTTP request with JSON data containing:
            - content: The current blog post content
            - title: The current blog post title (optional)
        
    Returns:
        JsonResponse with:
            - suggestions: Textual explanation of suggested improvements
            - improved_content: The complete improved blog post content
    """
    # Get API key and verify it's configured
    api_key = get_anthropic_api_key()
    
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Parse the request body
        data = json.loads(request.body)
        content = data.get('content', '')
        title = data.get('title', '')
        
        # Validate content
        if not content:
            return JsonResponse({
                'error': 'Content is required',
                'detail': 'Please provide content to improve.'
            }, status=400)
        
        # Craft system prompt
        system_message = """You are a professional blog editor specializing in improving content quality.
Your task is to analyze the provided blog post and suggest specific improvements for:
1. Structure: Flow, organization, headings, paragraphs
2. Content: Clarity, depth, engagement, value
3. Style: Tone, voice, readability
4. SEO: Keywords, meta description, title optimization
5. Formatting: Markdown usage, visual organization

Provide your response in TWO separate sections with clear markers:

SECTION 1: Improvement suggestions
- Provide specific, actionable feedback
- Identify strengths and areas for improvement
- Cover structure, content, style, SEO, and formatting
- Be constructive and specific

SECTION 2: Improved content
- Provide the complete improved blog post with your changes implemented
- Maintain proper markdown formatting
- Keep the same general structure but enhance as needed
- Preserve the author's voice and style while improving quality
- Include a suggested title if the current one can be improved

Your goal is to help the author create content that is engaging, valuable, and optimized for both readers and search engines.
"""

        # Craft user prompt
        user_prompt = f"""Please analyze and improve the following blog post:

Title: {title or "Untitled"}

Content:
```
{content}
```

Please provide both improvement suggestions and the revised content with your suggested changes.
"""

        # Prepare API request
        clean_api_key = api_key.strip().strip('"\'')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_api_key}",
            "anthropic-version": "2023-06-01",
            "x-api-key": clean_api_key
        }
        
        # Configure API request with optimized parameters
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,  # Set to maximum allowed for this model to handle longer responses
            "temperature": 0.7,  # Balanced creativity vs determinism
            "messages": [{"role": "user", "content": user_prompt}],
            "system": system_message
        }
        
        # Make the API request with extended timeout for large documents
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=request_body,
            timeout=180  # Increased timeout to 3 minutes to accommodate larger responses
        )
        
        # Handle API response errors
        if response.status_code != 200:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                    else:
                        error_message = str(error_data['error'])
            except Exception:
                error_message = f"API error: {response.status_code}"
                
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'status_code': response.status_code,
                'detail': "The Anthropic API returned an error. Please check the API key and try again."
            }, status=500)
        
        # Process the successful response
        response_data = response.json()
        ai_response = response_data['content'][0]['text']
        
        # Extract suggestions and improved content
        suggestions_match = re.search(r'SECTION 1:(?:\s*Improvement suggestions)?\s*([\s\S]*?)(?:SECTION 2:|$)', ai_response)
        improved_content_match = re.search(r'SECTION 2:(?:\s*Improved content)?\s*([\s\S]*)', ai_response)
        
        suggestions = suggestions_match.group(1).strip() if suggestions_match else "No specific suggestions provided."
        
        # Extract improved content
        if improved_content_match:
            improved_content_raw = improved_content_match.group(1).strip()
            # Check if the improved content is wrapped in code blocks
            content_block_match = re.search(r'```(?:markdown)?\s*([\s\S]*?)\s*```', improved_content_raw)
            if content_block_match:
                improved_content = content_block_match.group(1).strip()
            else:
                # If not in code blocks, use the raw content
                improved_content = improved_content_raw
        else:
            improved_content = None
        
        # Return suggestions and improved content
        result = {
            'suggestions': suggestions,
        }
        
        if improved_content:
            result['improved_content'] = improved_content
        
        return JsonResponse(result)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'detail': 'The request must include a valid JSON object.'
        }, status=400)
    except Exception as e:
        print(f"Error in ai_blog_improve_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error: {str(e)}",
            'detail': "An unexpected error occurred while analyzing your content."
        }, status=500)

@csrf_exempt
@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def markdown_preview_view(request):
    """
    API endpoint for rendering markdown content as HTML with scroll preservation.
    
    This view powers the real-time preview feature in the AI blog editor by:
    1. Accepting markdown content from the editor
    2. Converting it to HTML using the markdownify utility
    3. Returning the rendered HTML for display in the preview pane
    4. Supporting the scroll position preservation system
    
    The endpoint is designed for fast, frequent updates as the user types,
    with minimal processing to ensure responsive previews.
    
    Args:
        request: The HTTP request with JSON data containing 'content' field
        
    Returns:
        JsonResponse with the rendered HTML in the 'html' field
    """
    try:
        # Parse the request body
        data = json.loads(request.body)
        content = data.get('content', '')
        
        # Render markdown to HTML
        html = markdownify(content)
        
        return JsonResponse({
            'html': html
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'detail': 'The request must include a valid JSON object.'
        }, status=400)
    except Exception as e:
        print(f"Error in markdown_preview_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error: {str(e)}",
            'detail': "An unexpected error occurred while rendering the preview."
        }, status=500)

@login_required
@user_passes_test(is_staff)
def save_ai_blog_view(request):
    """
    View for saving a blog post created with the AI blog editor.
    
    This view handles the form submission from the AI blog editor and creates
    a new blog post or updates an existing one.
    
    Args:
        request: The HTTP request
        
    Returns:
        Redirect to the post edit page in admin
    """
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        author_id = request.POST.get('author', '')
        category_id = request.POST.get('category', '')
        status = request.POST.get('status', 'draft')
        
        # Validate required fields
        if not title or not content or not author_id:
            # Go back to the editor with an error
            return redirect('blog:ai_blog_editor')
        
        # Create a slug from the title
        slug = slugify(title)
        
        # Get the author
        try:
            author = User.objects.get(id=author_id)
        except User.DoesNotExist:
            # Go back to the editor with an error
            return redirect('blog:ai_blog_editor')
        
        # Get the category if provided
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                # Category is optional, so continue without it
                pass
        
        # Create the post
        post = Post(
            title=title,
            slug=slug,
            author=author,
            content=content,
            category=category,
            status=status,
        )
        
        # Save the post
        post.save()
        
        # Redirect to the post edit page in admin
        return redirect('admin:blog_post_change', post.id)
    
    # If not POST, redirect to the editor
    return redirect('blog:ai_blog_editor')

@login_required
@user_passes_test(is_staff)
def ai_post_generator_view(request):
    """
    View for the AI post generator interface.
    
    This view provides an admin interface with a form to generate blog posts
    using AI. It handles both the form display and post creation after generation.
    
    Args:
        request: The HTTP request
        
    Returns:
        Rendered template with the post generation form
    """
    # Check if API key is configured
    api_key = get_anthropic_api_key()
    api_key_configured = bool(api_key)
    
    if request.method == 'POST':
        form = AIPostGeneratorForm(request.POST)
        if form.is_valid():
            # Get form data
            title = request.POST.get('generated_title', '')
            content = request.POST.get('generated_content', '')
            slug = request.POST.get('generated_slug', '')
            
            if not title or not content:
                form.add_error(None, "Missing generated content. Please generate content before saving.")
                context = {
                    'form': form,
                    'api_key_configured': api_key_configured,
                }
                return render(request, 'blog/ai_post_generator.html', context)
            
            # Create new post object
            post = Post(
                title=title,
                slug=slug if slug else slugify(title),
                author=form.cleaned_data['author'],
                content=content,
                category=form.cleaned_data['category'],
                status='published' if form.cleaned_data['publish_directly'] else 'draft',
            )
            
            # Save the post
            post.save()
            
            # Redirect to the post edit page in admin
            return redirect('admin:blog_post_change', post.id)
    else:
        # Display empty form
        form = AIPostGeneratorForm()
    
    context = {
        'form': form,
        'api_key_configured': api_key_configured,
    }
    
    return render(request, 'blog/ai_post_generator.html', context)

@csrf_exempt
@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def generate_ai_post_view(request):
    """
    API endpoint for generating blog post content with AI.
    
    This view handles the AJAX request from the post generator interface and uses
    the Anthropic API to generate a blog post based on the provided parameters.
    
    Args:
        request: The HTTP request with JSON data containing post parameters
        
    Returns:
        JsonResponse with the generated content or error message
    """
    # Get API key and verify it's configured
    api_key = get_anthropic_api_key()
    
    if not api_key:
        return JsonResponse({
            'error': 'Anthropic API key not configured',
            'detail': 'Please add ANTHROPIC_API_KEY to your environment variables.'
        }, status=500)
    
    try:
        # Parse the request body
        data = json.loads(request.body)
        topic = data.get('topic', '')
        title = data.get('title', '')
        category_id = data.get('category', '')
        length = data.get('length', 'medium')
        tone = data.get('tone', 'informative')
        keywords = data.get('keywords', '')
        
        # Validate required fields
        if not topic:
            return JsonResponse({
                'error': 'Topic is required',
                'detail': 'Please provide a topic for the blog post.'
            }, status=400)
        
        # Get category name if provided
        category_name = ''
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category_name = category.name
            except Category.DoesNotExist:
                pass
        
        # Map length to word count
        word_count_map = {
            'short': 300,
            'medium': 600,
            'long': 1000
        }
        word_count = word_count_map.get(length, 600)
        
        # Format keywords as comma-separated list if provided
        keywords_formatted = f"Keywords to include: {keywords}" if keywords else ""
        
        # Craft prompt for the AI
        system_message = f"""You are a professional blog content creator who specializes in writing engaging, well-structured blog posts.
I'll provide details about the post I want you to create, and you'll generate high-quality content that follows markdown formatting.

Please provide your response in the following format:

```title
The blog post title here
```

```slug
url-friendly-slug-for-this-post
```

```content
The full blog post content in markdown format, including headings, lists, etc.
```

Important guidelines:
1. Create content that is informative, engaging, and valuable to readers
2. Use proper markdown formatting with headings, lists, emphasis, etc.
3. Include an introduction, body with multiple sections, and conclusion
4. Create a catchy, SEO-friendly title if none is provided
5. Generate a URL-friendly slug based on the title
6. Write in a {tone} tone
7. Target approximately {word_count} words in total
8. Format the content as professional markdown with proper headings (##, ###) and formatting
9. Use citations or references where appropriate
"""

        user_message = f"""Please write a blog post about: {topic}
        
{f"Title: {title}" if title else "Please generate an appropriate title"}
{f"Category: {category_name}" if category_name else ""}
{keywords_formatted}

The post should be {length} in length with a {tone} tone.
"""

        # Prepare API request
        clean_api_key = api_key.strip().strip('"\'')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_api_key}",
            "anthropic-version": "2023-06-01",
            "x-api-key": clean_api_key
        }
        
        request_body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": user_message}],
            "system": system_message
        }
        
        # Make the API request
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=request_body,
            timeout=120  # Longer timeout for longer content generation
        )
        
        # Handle API response errors
        if response.status_code != 200:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_message = error_data['error'].get('message', 'Unknown error')
                    else:
                        error_message = str(error_data['error'])
            except Exception:
                error_message = f"API error: {response.status_code}"
                
            return JsonResponse({
                'error': f"API Error: {error_message}",
                'status_code': response.status_code,
                'detail': "The Anthropic API returned an error. Please check the API key and try again."
            }, status=500)
        
        # Process the successful response
        response_data = response.json()
        ai_response = response_data['content'][0]['text']
        
        # Extract title, slug, and content sections
        title_match = re.search(r'```title\s*([\s\S]*?)\s*```', ai_response)
        slug_match = re.search(r'```slug\s*([\s\S]*?)\s*```', ai_response)
        content_match = re.search(r'```content\s*([\s\S]*?)\s*```', ai_response)
        
        # Extract and process the sections
        if title_match and content_match:
            extracted_title = title_match.group(1).strip()
            extracted_content = content_match.group(1).strip()
            
            # Extract slug or generate from title
            if slug_match:
                extracted_slug = slug_match.group(1).strip()
            else:
                extracted_slug = slugify(extracted_title)
            
            # Convert markdown to HTML for preview
            content_html = markdownify(extracted_content)
            
            # Return the generated content
            return JsonResponse({
                'title': extracted_title,
                'slug': extracted_slug,
                'content': extracted_content,
                'content_html': content_html
            })
        else:
            # If we couldn't extract the sections properly
            return JsonResponse({
                'error': 'Failed to parse AI response',
                'detail': 'The AI response was not in the expected format. Please try again.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'detail': 'The request must include a valid JSON object.'
        }, status=400)
    except Exception as e:
        print(f"Error in generate_ai_post_view: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'error': f"Error: {str(e)}",
            'detail': "An unexpected error occurred while generating the post."
        }, status=500)