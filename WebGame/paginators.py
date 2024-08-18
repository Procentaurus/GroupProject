from rest_framework.pagination import PageNumberPagination

from django.conf import settings


class GameArchivePaginator(PageNumberPagination):
    page_size = settings.ARCHIVE_LIST_ENDPOINT_PAGE_SIZE


class MyUserPaginator(PageNumberPagination):
    page_size = settings.MYUSER_LIST_ENDPOINT_PAGE_SIZE
