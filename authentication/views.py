from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from customers.serializers import CustomerRegistrationSerializer, CustomerSerializer
from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from oauth2_provider.contrib.rest_framework import TokenHasScope


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                CustomerSerializer(customer).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = CustomerSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = CustomerSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserInfoView(APIView):
    """
    Custom UserInfo endpoint (optional - django-oauth-toolkit provides one)
    """
    permission_classes = [IsAuthenticated, TokenHasScope]
    required_scopes = ['openid']
    
    def get(self, request):
        user = request.user
        token = request.auth
        
        userinfo_data = {
            'sub': str(user.id),
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'given_name': user.first_name or "",
            'family_name': user.last_name or "",
            'email': user.email,
            'email_verified': getattr(user, 'is_verified', False),
            'preferred_username': user.username,
        }
        
        # Add profile scope claims
        if 'profile' in token.scope.split():
            if hasattr(user, 'phone_number'):
                userinfo_data['phone_number'] = user.phone_number or ""
            if hasattr(user, 'address'):
                userinfo_data['address'] = user.address or ""
        
        return Response(userinfo_data)
    
def openid_configuration(request):
    base_url = request.build_absolute_uri('/').rstrip('/')

    return JsonResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/o/authorize/",
        "token_endpoint": f"{base_url}/o/token/",
        "userinfo_endpoint": f"{base_url}/api/auth/userinfo/",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "response_types_supported": [
            "code", "id_token", "token",
            "code id_token", "code token", "code id_token token"
        ],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email", "read", "write"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post", "client_secret_basic"
        ],
        "grant_types_supported": [
            "authorization_code", "implicit", "refresh_token"
        ],
    })

def jwks(request):
    # Load your private RSA key from settings
    private_key_pem = settings.OAUTH2_PROVIDER['OIDC_RSA_PRIVATE_KEY']
    
    key = jwk.JWK.from_pem(private_key_pem.encode())
    return JsonResponse({
        "keys": [json.loads(key.export(private_keys=False))]
    })



@protected_resource(scopes=['read'])
@require_http_methods(["GET"])
def protected_view(request):
    """Example protected view that requires OAuth2 token"""
    return JsonResponse({
        'message': 'Hello, OAuth2 world!',
        'user': request.user.username,
        'scopes': request.auth.scope.split()
    })


@csrf_exempt
@protected_resource(scopes=['write'])
@require_http_methods(["POST"])
def create_resource(request):
    """Example protected endpoint that requires write scope"""
    try:
        data = json.loads(request.body)
        return JsonResponse({
            'message': 'Resource created successfully',
            'data': data,
            'user': request.user.username
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
