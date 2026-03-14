from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet

from products.models import Product
from products.serializers import ProductSerializer


@extend_schema(tags=["Products"])
class ProductViewSet(BaseAuthViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"
