from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application, AccessToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test user, OAuth app, and access token for development'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='testuser', help='Username for test user')
        parser.add_argument('--token', default='test-token-123', help='Token value')

    def handle(self, *args, **options):
        username = options['username']
        token_value = options['token']
        
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': '+254712345678'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'✅ Created user: {username}')
        else:
            self.stdout.write(f'📋 Using existing user: {username}')

        # Create or get OAuth application
        app, created = Application.objects.get_or_create(
            name="Test API Client",
            defaults={
                'client_type': Application.CLIENT_PUBLIC,
                'authorization_grant_type': Application.GRANT_AUTHORIZATION_CODE,
            }
        )
        if created:
            self.stdout.write(f'✅ Created OAuth app: {app.name}')
        else:
            self.stdout.write(f'📋 Using existing OAuth app: {app.name}')
        
        self.stdout.write(f'📋 Client ID: {app.client_id}')

        # Create access token
        token, created = AccessToken.objects.get_or_create(
            token=token_value,
            defaults={
                'user': user,
                'application': app,
                'scope': 'read write openid'
            }
        )
        if created:
            self.stdout.write(f'✅ Created access token: {token.token}')
        else:
            self.stdout.write(f'📋 Using existing token: {token.token}')

        self.stdout.write('')
        self.stdout.write('🎯 Test your API with:')
        self.stdout.write(f'curl -X GET http://localhost:8000/api/products/ -H "Authorization: Bearer {token.token}"')