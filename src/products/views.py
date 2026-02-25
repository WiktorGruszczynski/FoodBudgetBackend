from foodbudget_core.views import BaseAuthViewSet
from rest_framework.response import Response

from products.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(BaseAuthViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request):
        pass

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        product = serializer.save()

        return Response(
            {
                "product": {
                    "id": product.id,
                },
                "message": f"Product [{product.name}] created successfully",
            },
            status=201,
        )
