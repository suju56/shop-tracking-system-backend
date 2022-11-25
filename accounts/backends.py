from .models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import datetime
import jwt
from django.conf import settings


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(access_token, settings.KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid Access Token")

        u_id = payload['user_id']
        user = User.objects.filter(id=u_id).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        if user.password[-30:] != payload["password"][-30:]:
            raise exceptions.AuthenticationFailed('Password changed.Please logged in again.')
        return user, None


def generate_access_token(user):
    access_token_payload = {
        'user_id': user.id,
        "is_superuser": user.is_superuser,
        "password": user.password,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, minutes=15),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        "password": user.password[-30:],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=20),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return refresh_token
