import logging
from datetime import timedelta

import requests
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from foodbudget_core.views import BaseAuthViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from products.models import Product
from products.serializers import ProductSerializer

logger = logging.getLogger(__name__)
SYNC_INTERVAL = timezone.now() - timedelta(days=1)


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

    def _fetch_from_external_api(self, ean: str):
        try:
            response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{ean}", timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == 0:
                return None

            product_data = data.get("product", {})
            nutriments = product_data.get("nutriments", {})

            if not nutriments:
                return None

            return {
                "name": product_data.get("product_name") or product_data.get("product_name_en"),
                "ean": ean,
                "quantity": None,
                "quantity_unit": product_data.get("serving_quantity_unit"),
                "manufacturer": product_data.get("brands"),
                "energy": nutriments.get("energy-kcal_100g"),
                "fat": nutriments.get("fat_100g"),
                "saturated_fat": nutriments.get("saturated-fat_100g"),
                "carbohydrates": nutriments.get("carbohydrates_100g"),
                "sugars": nutriments.get("sugars_100g"),
                "fiber": nutriments.get("fiber_100g"),
                "protein": nutriments.get("proteins_100g"),
                "salt": nutriments.get("salt_100g"),
            }

        except Exception:
            return None

    @action(detail=False, methods=["get"], url_path=r"ean/(?P<ean>\d+)")
    def retrieve_by_ean(self, request, ean=None):
        product_instance = Product.objects.filter(ean=ean).first()

        now = timezone.now()
        is_old = product_instance and (
            not product_instance.last_synced_at or product_instance.last_synced_at < (now - timedelta(days=1))
        )

        if not product_instance or is_old:
            external_data = self._fetch_from_external_api(ean)

            if external_data:
                return Response({"is_draft": True, "product": self.get_serializer(external_data).data})

        if not product_instance:
            return Response({"error": "Not found"}, status=404)

        serializer = self.get_serializer(product_instance)
        return Response({"is_draft": False, "product": serializer.data})
