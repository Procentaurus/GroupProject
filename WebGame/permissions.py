from rest_framework import permissions


class AccessHisData(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return True if obj.id == request.user.id else False


class ChoseGetMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return True if request.method == 'GET' else False


class ChosePutMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return True if request.method == 'PUT' else False


class ChosePostMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return True if request.method == 'POST' else False


class ChoseDeleteMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return True if request.method == 'DELETE' else False


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        print(request.user.is_admin)
        return True if request.user.is_admin else False
