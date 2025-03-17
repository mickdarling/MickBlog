import os
import sys
from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings

class Command(RunserverCommand):
    help = 'Runs the server with HTTPS using local certificates'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--cert-file',
            default=os.path.join(settings.BASE_DIR, 'certs', 'localhost+2.pem'),
            help='Path to the certificate file'
        )
        parser.add_argument(
            '--key-file',
            default=os.path.join(settings.BASE_DIR, 'certs', 'localhost+2-key.pem'),
            help='Path to the key file'
        )

    def handle(self, *args, **options):
        # Set environment variable for Django's runserver to use SSL
        os.environ['DJANGO_HTTPS'] = 'on'
        
        # Pass the certificate and key file to the server
        self.cert_file = options.get('cert_file')
        self.key_file = options.get('key_file')
        
        # Check if certificates exist
        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            self.stderr.write(self.style.ERROR(
                f"Certificate files not found. Make sure they exist at:"
                f"\n- {self.cert_file}\n- {self.key_file}"
            ))
            sys.exit(1)
        
        # Show helpful message
        self.stdout.write(self.style.SUCCESS(
            f"Starting HTTPS server with certificates:\n"
            f"- Certificate: {self.cert_file}\n"
            f"- Key: {self.key_file}\n"
        ))
        
        # Start server with SSL
        options['ssl_certificate'] = self.cert_file
        options['ssl_key'] = self.key_file
        
        super().handle(*args, **options)