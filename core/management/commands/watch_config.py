import os
import time
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.models import SiteConfig

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, command_path):
        self.command_path = command_path
        self.last_modified = time.time()
        
    def on_modified(self, event):
        if event.src_path.endswith('site_config.md'):
            # Debounce to prevent multiple executions
            if time.time() - self.last_modified > 1:
                self.last_modified = time.time()
                print(f"\n🔄 {event.src_path} has been modified - updating site configuration...")
                subprocess.call(['python', self.command_path, 'update_site_config'])
                print("✅ Site configuration updated from file!\n")

class Command(BaseCommand):
    help = 'Watches the site_config.md file for changes and auto-updates site configuration'
    
    def handle(self, *args, **options):
        config_file = os.path.join(settings.BASE_DIR, 'site_config.md')
        
        # Check if file exists
        if not os.path.exists(config_file):
            self.stdout.write(self.style.ERROR(f'Config file not found: {config_file}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Watching {config_file} for changes...'))
        self.stdout.write(self.style.SUCCESS('Any saved changes will automatically update the site configuration.'))
        self.stdout.write(self.style.SUCCESS('Changes made in admin will also update the config file.'))
        self.stdout.write(self.style.SUCCESS('Press Ctrl+C to stop watching.'))
        
        # Set up file watching
        event_handler = ConfigFileHandler(os.path.join(settings.BASE_DIR, 'manage.py'))
        observer = Observer()
        observer.schedule(event_handler, path=settings.BASE_DIR, recursive=False)
        observer.start()
        
        # Run the export once at startup to make sure the file is in sync
        print("Syncing site_config.md with current database values...")
        subprocess.call(['python', os.path.join(settings.BASE_DIR, 'manage.py'), 'export_site_config'])
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()