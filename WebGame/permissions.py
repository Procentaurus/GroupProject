from rest_framework import permissions


class IsTheVeryUser(permissions.BasePermission): # checks if the user, who requested particular object is its owner

    def has_object_permission(self, request, view, obj):
        if obj.id == request.user.id:
            return True
        else:
            return False
        
class ChoseSafeMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD']:
            return True
        else:
            return False
        

class IsAdmin(permissions.BasePermission): 
    def has_permission(self, request, view):
        return True if request.user.is_admin else False

