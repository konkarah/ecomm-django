# from oauth2_provider.oauth2_validators import OAuth2Validator


# class CustomOAuth2Validator(OAuth2Validator):
#     def get_default_scopes(self, client_id, request, *args, **kwargs):
#         """
#         Return a list of default scopes for the client
#         """
#         return ['read']
    
#     def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
#         """
#         Return the default redirect URI for the client
#         """
#         return 'http://localhost:3000/callback'

from oauth2_provider.oauth2_validators import OAuth2Validator
from django.contrib.auth import authenticate


class CustomOAuth2Validator(OAuth2Validator):
    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """
        Return a list of default scopes for the client
        """
        return ['read']
    
    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        """
        Return the default redirect URI for the client
        """
        try:
            from oauth2_provider.models import Application
            application = Application.objects.get(client_id=client_id)
            return application.redirect_uris.split().pop() if application.redirect_uris else None
        except Application.DoesNotExist:
            return None
    
    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        Ensure requested scopes are within allowed scope of the client
        """
        allowed_scopes = ['read', 'write', 'openid', 'profile', 'email']
        return all((s in allowed_scopes for s in scopes))
    
    def get_additional_claims(self, request):
        """
        Add additional claims to ID tokens
        """
        return {
            'aud': request.client.client_id,
            'iss': 'http://localhost:8000',  # Change to your domain
            'auth_time': int(request.user.last_login.timestamp()) if request.user.last_login else None,
        }
    
    def validate_silent_authorization(self, request):
        """
        Determine if silent authorization is allowed
        """
        return True
    
    def validate_user_match(self, id_token_hint, scopes, claims, request):
        """
        Ensure the user matches the id_token_hint
        """
        return True