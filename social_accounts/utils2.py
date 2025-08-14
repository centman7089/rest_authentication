from google.auth.transport.requests import Request
from google.oauth2 import id_token
from .models import User
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class Google:
    # Verify token coming from Google
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, Request())
            # Verify if the token is actually from Google
            if "accounts.google.com" in id_info.get("iss", ""):
                return id_info
        except Exception:
            return "token is invalid or expired"


def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            # Login user
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
                detail=f'Please continue your login with {user[0].auth_provider}'
            )
    else:
        # Register new social user
        new_user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_AUTH_PASSWORD
        }
        register_user = User.objects.create_user(**new_user)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()

        login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
        user_tokens = login_user.tokens()
        return {
            'email': login_user.email,
            'full_name': login_user.get_full_name,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }
