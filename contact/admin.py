from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at', 'read')
    list_filter = ('sent_at', 'read')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'sent_at'
    ordering = ('-sent_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'sent_at', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        # Prevent adding contacts manually
        return False