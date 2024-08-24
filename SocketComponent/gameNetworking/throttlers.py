from rest_framework.throttling import UserRateThrottle


class GameAuthenticationTokenCreateHourRate(UserRateThrottle):
    scope = 'gametoken_create_throttle_hour_rate'
