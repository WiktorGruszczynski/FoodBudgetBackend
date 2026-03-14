from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet
from rest_framework import permissions

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


class IsRecipeCreatorOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to read recipe and use it.
    Only creator can modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.issued_by is not None and obj.issued_by == request.user


@extend_schema(tags=["Recipes"])
class RecipeViewSet(BaseAuthViewSet):
    queryset = Recipe.objects.prefetch_related("ingredients").all()
    serializer_class = RecipeSerializer

    def get_permissions(self):
        return [*super().get_permissions(), IsRecipeCreatorOrReadOnly()]
