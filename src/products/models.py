import json
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from foodbudget_core.services import MeasurmentUnit


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True, default=None)
    manufacturer = models.CharField(max_length=128, blank=True, default="")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="products")
    recipe = models.OneToOneField("recipes.Recipe", on_delete=models.CASCADE, related_name="product", null=True, blank=True)

    # measurments
    quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)
    nutrient_unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)
    density = models.FloatField(null=True, blank=True)

    # nutrients
    # values below are in (grams) per 100g/100ml
    energy_kcal = models.FloatField(null=True, blank=True)

    fat = models.FloatField(null=True, blank=True)
    saturated_fat = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)
    sugars = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    salt = models.FloatField(null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(ean__isnull=True) | Q(recipe__isnull=True), name="product_ean_or_recipe_exclusive"
            )
        ]

    def __str__(self):
        data = {key: str(value) if key == "id" else value for key, value in self.__dict__.items() if not key.startswith("_")}

        return json.dumps(data, indent=4, ensure_ascii=False)
