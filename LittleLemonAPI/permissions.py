from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Manager").exists():
            return True
        
        raise PermissionDenied({"message":"Unauthorized"})
    
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name="Manager").exists():
            return True
        
        raise PermissionDenied({"message":"Unauthorized"})
    
class IsManagerPostOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        edit_methods = ("POST")
        if request.method in edit_methods and request.user.groups.filter(name="Manager").exists():
            return True
        
        raise PermissionDenied({"message":"Unauthorized"})
    
    def has_object_permission(self, request, view, obj):
        return False


class IsManagerEditOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        edit_methods = ("POST","PUT","PATCH","DELETE")
        if request.method in edit_methods and not request.user.groups.filter(name="Manager").exists():
            raise PermissionDenied({"message":"Unauthorized"})
        return True
    
    def has_object_permission(self, request, view, obj):
        edit_methods = ("PUT","PATCH","DELETE")
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.method in edit_methods and request.user.groups.filter(name="Manager").exists():
            return True
        
        raise PermissionDenied({"message":"Unauthorized"})