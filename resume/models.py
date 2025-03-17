from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = MarkdownxField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-end_date']
        verbose_name_plural = "Education"
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"
    
    @property
    def formatted_description(self):
        return markdownify(self.description)


class Experience(models.Model):
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = MarkdownxField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    @property
    def formatted_description(self):
        return markdownify(self.description)


class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('technical', 'Technical Skills'),
        ('soft', 'Soft Skills'),
        ('languages', 'Languages'),
        ('tools', 'Tools & Platforms'),
        ('other', 'Other Skills'),
    )
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    proficiency = models.IntegerField(default=75, help_text="Skill proficiency 0-100")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date_obtained = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-date_obtained']
    
    def __str__(self):
        return f"{self.name} from {self.issuer}"