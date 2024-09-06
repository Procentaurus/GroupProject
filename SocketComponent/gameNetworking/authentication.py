from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.settings import api_settings


class NonUserJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token: Token):
        user_id = None
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            is_admin = validated_token.get('is_admin', False)
        except KeyError:
            raise InvalidToken(
                ("Token contained no recognizable user identification"))
        return (user_id, is_admin)
