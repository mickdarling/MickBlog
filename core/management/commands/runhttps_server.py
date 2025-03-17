import os
import ssl
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import WSGIServer

class SecureWSGIServer(WSGIServer):
    def __init__(self, *args, **kwargs):
        cert_file = kwargs.pop('cert_file', None)
        key_file = kwargs.pop('key_file', None)
        
        super().__init__(*args, **kwargs)
        
        if cert_file and key_file:
            self.socket = ssl.wrap_socket(
                self.socket,
                certfile=cert_file,
                keyfile=key_file,
                server_side=True,
                ssl_version=ssl.PROTOCOL_TLS_SERVER,
            )

class Command(RunserverCommand):
    help = 'Runs the server with HTTPS using local certificates'
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--cert-file',
            default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               '../../../certs/localhost+2.pem'),
            help='Path to certificate file'
        )
        parser.add_argument(
            '--key-file',
            default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              '../../../certs/localhost+2-key.pem'),
            help='Path to key file'
        )
    
    def get_handler(self, *args, **options):
        handler = super().get_handler(*args, **options)
        return handler
        
    def handle(self, *args, **options):
        # Store certificate file paths
        self.cert_file = options.get('cert_file')
        self.key_file = options.get('key_file')
        
        # Print certificate paths
        self.stdout.write(f"Using certificate: {self.cert_file}")
        self.stdout.write(f"Using key file: {self.key_file}")
        
        super().handle(*args, **options)
    
    def inner_run(self, *args, **options):
        # Replace the WSGIServer with our secure version
        from django.core.servers.basehttp import WSGIServer as origWSGIServer
        from django.core.servers.basehttp import WSGIRequestHandler
        
        # Store the original WSGIServer
        original_wsgi_server = origWSGIServer
        
        try:
            # Make SecureWSGIServer available at the module level
            from django.core.servers import basehttp
            basehttp.WSGIServer = SecureWSGIServer
            basehttp.WSGIServer.cert_file = self.cert_file
            basehttp.WSGIServer.key_file = self.key_file
            
            # Call the original method
            super().inner_run(*args, **options)
        finally:
            # Restore the original WSGIServer
            from django.core.servers import basehttp
            basehttp.WSGIServer = original_wsgi_server