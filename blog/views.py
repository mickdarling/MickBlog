from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Category
from core.models import SiteConfig

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