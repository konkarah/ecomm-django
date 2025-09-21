from django.core.management.base import BaseCommand
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = 'Create OAuth2 application for development'
    
    def add_arguments(self, parser):
        parser.add_argument('--name', default='E-commerce API Client')
        parser.add_argument('--client-type', choices=['confidential', 'public'], default='public')
        parser.add_argument('--grant-type', 
                          choices=['authorization-code', 'client-credentials'], 
                          default='authorization-code')
    
    def handle(self, *args, **options):
        app = Application.objects.create(
            name=options['name'],
            client_type=Application.CLIENT_PUBLIC if options['client_type'] == 'public' else Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE if options['grant_type'] == 'authorization-code' else Application.GRANT_CLIENT_CREDENTIALS,
            skip_authorization=True,  # For development
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'OAuth2 Application created successfully!\n'
                f'Client ID: {app.client_id}\n'
                f'Client Secret: {app.client_secret}\n'
            )
        )
