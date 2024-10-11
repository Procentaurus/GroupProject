from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.settings import api_settings


class NonUserJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token: Token):
        try:
            user_id = validated_token.get(api_settings.USER_ID_CLAIM)
            is_admin = validated_token.get('is_admin', False)
            if not user_id:
                raise InvalidToken("Invalid token") 
            else: return (user_id, is_admin)
        except KeyError:
            raise InvalidToken(
                "Token contained no recognizable user identification.")

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return (self.get_user(validated_token), None)
