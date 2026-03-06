from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet


@extend_schema(tags=["Recipes"])
class RecipeViewSet(BaseAuthViewSet):
    pass
