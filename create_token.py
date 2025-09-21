import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from oauth2_provider.models import Application, AccessToken

User = get_user_model()

def create_test_setup():
    # Create user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+254712345678'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f'✅ Created user: {user.username}')
    else:
        print(f'📋 Using existing user: {user.username}')

    # Create OAuth app
    app, created = Application.objects.get_or_create(
        name="Test API Client",
        defaults={
            'client_type': Application.CLIENT_PUBLIC,
            'authorization_grant_type': Application.GRANT_AUTHORIZATION_CODE,
        }
    )
    if created:
        print(f'✅ Created OAuth app: {app.name}')
    else:
        print(f'📋 Using existing OAuth app: {app.name}')

    print(f'📋 Client ID: {app.client_id}')

    # Create token
    token, created = AccessToken.objects.get_or_create(
        token='test-token-123',
        defaults={
            'user': user,
            'application': app,
            'scope': 'read write openid'
        }
    )
    if created:
        print(f'✅ Created access token: {token.token}')
    else:
        print(f'📋 Using existing token: {token.token}')

    print('\n🎯 Test your API with:')
    print(f'curl -X GET http://localhost:8000/api/products/ -H "Authorization: Bearer {token.token}"')

if __name__ == '__main__':
    create_test_setup()