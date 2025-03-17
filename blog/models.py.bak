from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Category(models.Model):
    """
    Blog post category model for organizing content.
    
    Categories provide a way to group related blog posts together and improve
    site navigation. Each category has a unique name and slug for URLs.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category display name")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly version of the category name")
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the URL for viewing all posts in this category.
        Uses the named URL pattern 'blog:category' with the slug as parameter.
        """
        return reverse('blog:category', kwargs={'slug': self.slug})


class Post(models.Model):
    """
    Blog post model supporting markdown content, categories, and publishing workflow.
    
    Posts are the primary content type for the blog section. They support markdown
    formatting, draft/published status, and categorization. Each post has
    a URL that includes its publication date and slug for better SEO.
    """
    # Status choices for publishing workflow
    STATUS_CHOICES = (
        ('draft', 'Draft'),      # Not publicly visible
        ('published', 'Published'),  # Publicly visible
    )
    
    # Core post fields
    title = models.CharField(max_length=250, help_text="Post title")
    slug = models.SlugField(max_length=250, unique_for_date='publish', 
                         help_text="URL-friendly version of the title (must be unique for publication date)")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts',
                            help_text="User who wrote this post")
    content = MarkdownxField(help_text="Post content in Markdown format")
    summary = models.TextField(blank=True, help_text="Optional manual summary (if blank, auto-generated from content)")
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='posts', 
                              null=True, blank=True, help_text="Optional category for grouping related posts")
    
    # Date and time fields
    publish = models.DateTimeField(default=timezone.now, help_text="Publication date and time")
    created = models.DateTimeField(auto_now_add=True, help_text="When the post was first created")
    updated = models.DateTimeField(auto_now=True, help_text="When the post was last updated")
    
    # Publishing status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft',
                           help_text="Draft posts are only visible to admin users")
    
    class Meta:
        ordering = ('-publish',)  # Newest posts first
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """
        Returns the canonical URL for this post.
        
        The URL pattern includes the publication date (year/month/day) and slug,
        which creates semantic URLs that are good for SEO and provide a logical structure.
        """
        return reverse('blog:post_detail', args=[self.publish.year,
                                                self.publish.month,
                                                self.publish.day,
                                                self.slug])
    
    @property
    def formatted_content(self):
        """
        Returns the content field rendered from Markdown to HTML.
        This property is used in templates to display the formatted post content.
        """
        return markdownify(self.content)
    
    @property
    def formatted_summary(self):
        """
        Returns a formatted HTML summary of the post.
        
        If a manual summary is provided, it will be used; otherwise,
        the first 200 characters of the post content will be used with
        an ellipsis appended. This is useful for post list views.
        """
        # Use summary if available, otherwise use first 200 chars of content
        text = self.summary if self.summary else self.content
        if len(text) > 200:
            return markdownify(text[:200] + "...")
        return markdownify(text)