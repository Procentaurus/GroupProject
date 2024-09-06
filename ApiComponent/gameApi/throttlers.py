from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.conf import settings


class MyUserListThrottleMinRate(UserRateThrottle):
    scope = 'myuser_list_throttle_min_rate'


class MyUserGetThrottleMinRate(UserRateThrottle):
    scope = 'myuser_get_throttle_min_rate'


class ArchiveListThrottleMinRate(UserRateThrottle):
    scope = 'archive_list_throttle_min_rate'


class ArchiveListThrottleDayRate(UserRateThrottle):
    scope = 'archive_list_throttle_day_rate'


class MyUserListThrottleDayRate(UserRateThrottle):
    scope = 'myuser_list_throttle_day_rate'


class MyUserGetThrottleDayRate(UserRateThrottle):
    scope = 'myuser_get_throttle_day_rate'


class MyUserCreateThrottleDayRate(UserRateThrottle):
    scope = 'myuser_create_throttle_day_rate'


class MyUserUpdateThrottleDayRate(UserRateThrottle):
    scope = 'myuser_update_throttle_day_rate'


class MyUserDeleteThrottleDayRate(UserRateThrottle):
    scope = 'myuser_delete_throttle_day_rate'


class CustomTokenCreateAnonHourRate(AnonRateThrottle):
    scope = 'customtoken_create_throttle_anon_hour_rate'


class CustomTokenCreateHourRate(UserRateThrottle):
    scope = 'customtoken_create_throttle_hour_rate'


class CustomTokenRotateHourRate(UserRateThrottle):
    scope = 'customtoken_rotate_throttle_hour_rate'


class CustomTokenRotateDayRate(UserRateThrottle):
    scope = 'customtoken_rotate_throttle_day_rate'
