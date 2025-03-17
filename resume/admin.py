from django.contrib import admin
from .models import Education, Experience, Skill, Certification
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Education)
class EducationAdmin(MarkdownxModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'order')
    list_filter = ('start_date', 'end_date')
    search_fields = ('institution', 'degree', 'field_of_study')
    ordering = ('order', '-end_date')

@admin.register(Experience)
class ExperienceAdmin(MarkdownxModelAdmin):
    list_display = ('position', 'company', 'location', 'start_date', 'end_date', 'current', 'order')
    list_filter = ('start_date', 'end_date', 'current')
    search_fields = ('position', 'company', 'location', 'description')
    ordering = ('order', '-start_date')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'order')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'order', 'name')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'date_obtained', 'expiration_date', 'order')
    list_filter = ('date_obtained', 'issuer')
    search_fields = ('name', 'issuer')
    ordering = ('order', '-date_obtained')