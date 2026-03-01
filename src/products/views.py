from foodbudget_core.views import BaseAuthViewSet
from rest_framework.response import Response

from products.models import Product
from products.permissions import IsProductOwnerOrReadOnly
from products.serializers import ProductSerializer


class ProductViewSet(BaseAuthViewSet):
    permission_classes = BaseAuthViewSet.permission_classes + [IsProductOwnerOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    # read methods

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    # modyfing methods

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"request": request})

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        product = serializer.save()

        return Response(
            {
                "product": {"id": product.id},
                "message": f"Product [{product.name}] updated successfully",
            },
            status=200,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        product_name = instance.name

        instance.delete()

        return Response({"message": f"Product [{product_name}] deleted successfully"}, status=200)
