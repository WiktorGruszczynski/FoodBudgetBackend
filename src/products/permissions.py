from rest_framework import permissions


class IsProductOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissions are:
        Read methods: Authenticated users
        Modify methods: Owner (issued_by)
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS - allow everyone who is authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT, PATCH, DELETE
        return obj.issued_by == request.user
