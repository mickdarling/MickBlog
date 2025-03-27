"""
Management command to test the version history functionality.
"""
import reversion
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SiteConfig

class Command(BaseCommand):
    help = 'Test the version history and recovery functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Starting Version History Test ==="))
        
        # Get the admin user (or create if needed)
        try:
            admin_user = User.objects.get(username="admin")
            self.stdout.write(f"Using existing admin user: {admin_user.username}")
        except User.DoesNotExist:
            self.stdout.write("Admin user not found. Creating...")
            admin_user = User.objects.create_superuser(
                username="admin", 
                email="admin@example.com", 
                password="admin"
            )
        
        # Get the site config
        config = SiteConfig.get()
        original_title = config.title
        original_css = config.custom_css
        self.stdout.write(f"Original title: {original_title}")
        
        # Create a version with a first change
        with reversion.create_revision():
            config.title = "Version 1 Test Title"
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Test version 1")
        self.stdout.write(self.style.SUCCESS("Created version 1"))
        
        # Create a version with a second change
        with reversion.create_revision():
            config.title = "Version 2 Test Title"
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Test version 2")
        self.stdout.write(self.style.SUCCESS("Created version 2"))
        
        # Create a version with a third change
        with reversion.create_revision():
            config.title = "Version 3 Test Title"
            config.custom_css = "body { background-color: #f00; }"
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Test version 3 with CSS")
        self.stdout.write(self.style.SUCCESS("Created version 3"))
        
        # List all versions
        self.stdout.write("\nAll versions:")
        versions = reversion.models.Version.objects.get_for_object(config)
        for i, version in enumerate(versions[0:5]):  # Show only the 5 most recent
            self.stdout.write(f"Version {i+1}: {version.revision.date_created} - {version.revision.comment}")
        
        # Test recovery of the first version
        self.stdout.write(self.style.WARNING("\nTesting recovery of version 1..."))
        version_to_recover = versions.last()  # Get the earliest version (version 1)
        
        # Get the data from the version
        version_data = version_to_recover.field_dict
        self.stdout.write(f"Version 1 title: {version_data.get('title')}")
        
        # Update the config with the version data
        with reversion.create_revision():
            for field_name, value in version_data.items():
                if hasattr(config, field_name):
                    setattr(config, field_name, value)
            
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Recovered version 1")
        
        # Verify the recovery
        config.refresh_from_db()
        self.stdout.write(f"After recovery, title is: {config.title}")
        self.stdout.write(f"CSS after recovery: {config.custom_css[:30]}..." if config.custom_css else "No CSS")
        
        # Test another recovery to version 3
        self.stdout.write(self.style.WARNING("\nTesting recovery of version 3..."))
        versions = reversion.models.Version.objects.get_for_object(config)
        version_to_recover = versions[2]  # Should be version 3
        
        # Get the data from the version
        version_data = version_to_recover.field_dict
        self.stdout.write(f"Version 3 title: {version_data.get('title')}")
        self.stdout.write(f"Version 3 CSS: {version_data.get('custom_css')[:30]}...")
        
        # Update the config with the version data
        with reversion.create_revision():
            for field_name, value in version_data.items():
                if hasattr(config, field_name):
                    setattr(config, field_name, value)
            
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Recovered version 3")
        
        # Verify the recovery
        config.refresh_from_db()
        self.stdout.write(f"After recovery to version 3, title is: {config.title}")
        self.stdout.write(f"CSS after recovery: {config.custom_css[:30]}..." if config.custom_css else "No CSS")
        
        # Finally, restore the original title and css
        with reversion.create_revision():
            config.title = original_title
            config.custom_css = original_css
            config.save()
            reversion.set_user(admin_user)
            reversion.set_comment("Restored original configuration")
        self.stdout.write(self.style.SUCCESS("Restored original configuration"))
        
        self.stdout.write(self.style.SUCCESS("\n=== Version History Test Complete ==="))