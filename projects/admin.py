from django.contrib import admin
from .models import Technology, Project
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Project)
class ProjectAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'featured')
    list_filter = ('status', 'featured', 'technologies')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'image')
        }),
        ('Status and Dates', {
            'fields': ('status', 'featured', 'start_date', 'end_date')
        }),
        ('URLs', {
            'fields': ('project_url', 'github_url')
        }),
        ('Technologies', {
            'fields': ('technologies',)
        }),
    )