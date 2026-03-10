from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


@extend_schema(tags=["Recipes"])
class RecipeViewSet(BaseAuthViewSet):
    queryset = Recipe.objects.prefetch_related("ingredients").all()
    serializer_class = RecipeSerializer

    # Rest of the endpoints are implemented automatically or by the serializer

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()

        if recipe.issued_by != request.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
