from rest_framework.throttling import SimpleRateThrottle


class CustomUserRateThrottle(SimpleRateThrottle):

    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user is None or not isinstance(request.user, tuple):
            ident = self.get_ident(request)
        else:
            id, _ = request.user
            ident = id if id else self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class GameAuthenticationTokenCreateHourRate(CustomUserRateThrottle):
    scope = 'gametoken_create_throttle_hour_rate'
