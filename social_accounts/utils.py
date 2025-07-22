from google.auth.transport import request
from google.oauth2 import id_token
from .models import User
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class Google():
    
    # to verify token coming from google
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, request.Request())
            # verify if the token is actually coming from google
            if "accounts.google.com" in id_info["iss"]: # actually stores the full part like https://accounts.google.co
                return id_info
                
        except Exception as e:
            return  "token is invalid or expired"
        
# def login_social_user(email,password):
#     user = authenticate(email=email, password=password)
#     user_tokens = user.tokens()
#     return {
#         'email': user.email,
#         'full_name': user.get_full_name,
#         'access_token': str(user_tokens.get('access')),
#         'refresh_token': str(user_tokens.get('refresh'))
#     }
    
        
def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            # login_social_user(email, settings.SOCIAL_AUTH_PASSWORD) method 2
            login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
            user_tokens = login_user.tokens()
            return {
            'email': login_user.email,
            'full_name': login_user.get_full_name,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
            }
        else:
            raise AuthenticationFailed(
                detail = f'please continue your login with {user[0].auth_provider}'
            )
    else:
        new_user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_AUTH_PASSWORD
        }
        register_user = User.objects.create_user(**new_user)
        register_user.auth_provider= provider
        register_user.is_verified= True
        register_user.save()
        # login_social_user(email=register_user.email, settings.SOCIAL_AUTH_PASSWORD) method 2
        login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
        user_tokens = login_user.tokens()
        return {
            'email': login_user.email,
            'full_name': login_user.get_full_name,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }
        