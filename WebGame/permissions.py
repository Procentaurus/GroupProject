from rest_framework import permissions


class AccessHisData(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return True if obj.id == request.user.id else False


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return True if request.user.is_admin else False
