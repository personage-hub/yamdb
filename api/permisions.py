from rest_framework import permissions


class AdminUrlUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'admin'
                or request.user.is_superuser)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_safe = request.method in permissions.SAFE_METHODS
        is_auth = request.user.is_authenticated
        return is_safe or is_auth

    def has_object_permission(self, request, view, obj):
        is_safe = request.method in permissions.SAFE_METHODS
        is_author = obj.author == request.user
        is_privileged = None
        if request.user.is_authenticated:
            is_privileged = request.user.role in ('moderator', 'admin')
        return is_author or is_safe or is_privileged
