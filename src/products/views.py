import logging

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet
from rest_framework.response import Response

from products.models import Product
from products.serializers import ProductSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=["Products"])
class ProductViewSet(BaseAuthViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def create(self, request):
        set_synced = request.data.get("set_synced", False)
        serializer = self.get_serializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        product = serializer.save()

        if set_synced:
            product.last_synced_at = timezone.now()
            product.save(update_fields=["last_synced_at"])

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
        set_synced = request.data.get("set_synced", False)

        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"request": request})

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        product = serializer.save()

        if set_synced:
            product.last_synced_at = timezone.now()
            product.save(update_fields=["last_synced_at"])

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
