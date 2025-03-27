"""
Test script for the version history functionality.

This script directly tests the SiteConfig recovery functionality by making changes
to the SiteConfig model, creating versions, and testing recovery.

Usage:
python manage.py shell < core/test_version_history.py
"""

import sys
import reversion
from django.contrib.auth.models import User
from core.models import SiteConfig

def main():
    """Run the version history test"""
    print("=== Starting Version History Test ===")
    
    # Enable console output
    import sys
    sys.stdout = sys.__stdout__
    
    # Get the admin user (or create if needed)
    try:
        admin_user = User.objects.get(username="admin")
        print(f"Using existing admin user: {admin_user.username}")
    except User.DoesNotExist:
        print("Admin user not found. Creating...")
        admin_user = User.objects.create_superuser(
            username="admin", 
            email="admin@example.com", 
            password="admin"
        )
    
    # Get the site config
    config = SiteConfig.get()
    original_title = config.title
    print(f"Original title: {original_title}")
    
    # Create a version with a first change
    with reversion.create_revision():
        config.title = "Version 1 Test Title"
        config.save()
        reversion.set_user(admin_user)
        reversion.set_comment("Test version 1")
    
    # Create a version with a second change
    with reversion.create_revision():
        config.title = "Version 2 Test Title"
        config.save()
        reversion.set_user(admin_user)
        reversion.set_comment("Test version 2")
    
    # Create a version with a third change
    with reversion.create_revision():
        config.title = "Version 3 Test Title"
        config.custom_css = "body { background-color: #f00; }"
        config.save()
        reversion.set_user(admin_user)
        reversion.set_comment("Test version 3 with CSS")
    
    # List all versions
    print("\nAll versions:")
    versions = reversion.models.Version.objects.get_for_object(config)
    for i, version in enumerate(versions):
        print(f"Version {i+1}: {version.revision.date_created} - {version.revision.comment}")
    
    # Test recovery of the first version
    print("\nTesting recovery of version 1...")
    version_to_recover = versions.last()  # Get the earliest version (version 1)
    
    # Get the data from the version
    version_data = version_to_recover.field_dict
    print(f"Version 1 title: {version_data.get('title')}")
    
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
    print(f"After recovery, title is: {config.title}")
    
    # Check that original CSS was preserved (if it was blank in version 1)
    print(f"CSS after recovery: {config.custom_css[:30]}..." if config.custom_css else "No CSS")
    
    # Test another recovery to version 3
    print("\nTesting recovery of version 3...")
    versions = reversion.models.Version.objects.get_for_object(config)
    version_to_recover = versions[2]  # Should be version 3
    
    # Get the data from the version
    version_data = version_to_recover.field_dict
    print(f"Version 3 title: {version_data.get('title')}")
    print(f"Version 3 CSS: {version_data.get('custom_css')[:30]}...")
    
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
    print(f"After recovery to version 3, title is: {config.title}")
    print(f"CSS after recovery: {config.custom_css[:30]}..." if config.custom_css else "No CSS")
    
    # Finally, restore the original title
    with reversion.create_revision():
        config.title = original_title
        config.custom_css = ""  # Clear test CSS
        config.save()
        reversion.set_user(admin_user)
        reversion.set_comment("Restored original configuration")
    
    print("\n=== Version History Test Complete ===")

if __name__ == "__main__":
    main()
    sys.exit(0)