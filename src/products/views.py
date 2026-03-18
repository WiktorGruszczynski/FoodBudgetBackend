from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet

from products.models import Product
from products.serializers import ProductSerializer


@extend_schema(tags=["Products"])
class ProductViewSet(BaseAuthViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.query_params.get("query")

        if query is not None and len(query) >= 3:
            queryset = queryset.filter(name__icontains=query)

        return queryset
