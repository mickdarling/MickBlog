from django.db import models
from django.utils import timezone


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.subject} from {self.name}"