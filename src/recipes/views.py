from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet
from rest_framework import permissions, status
from rest_framework.response import Response

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


class IsRecipeCreatorOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to read recipe and use it.
    Only creator can modify it.
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

    # Rest of the endpoints are implemented automatically or by the serializer
    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        recipe.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
