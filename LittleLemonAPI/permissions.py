from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsManagerPostOrReadOnly(permissions.DjangoModelPermissionsOrAnonReadOnly):
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


class IsManagerEditOrReadOnly(permissions.DjangoModelPermissionsOrAnonReadOnly):
    
    def has_permission(self, request, view):
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