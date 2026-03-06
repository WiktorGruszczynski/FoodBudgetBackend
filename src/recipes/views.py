from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet

from recipes.models import Recipe


@extend_schema(tags=["Recipes"])
class RecipeViewSet(BaseAuthViewSet):
    queryset = Recipe.objects.all()
