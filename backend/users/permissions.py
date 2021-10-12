from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            obj.author == request.user or request.method in SAFE_METHODS
        )
