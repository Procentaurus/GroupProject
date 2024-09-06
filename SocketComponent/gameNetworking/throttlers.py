from rest_framework.throttling import SimpleRateThrottle


class CustomUserRateThrottle(SimpleRateThrottle):

    scope = 'user'

    def get_cache_key(self, request, view):
        id, _ = request.user
        if id:
            ident = id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class GameAuthenticationTokenCreateHourRate(CustomUserRateThrottle):
    scope = 'gametoken_create_throttle_hour_rate'
