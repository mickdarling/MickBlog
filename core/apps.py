from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Import admin_site module on startup to ensure
        SiteConfig model is registered in the admin.
        """
        import core.admin_site
