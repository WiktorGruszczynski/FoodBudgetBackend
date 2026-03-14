import json
import uuid

from django.conf import settings
from django.db import models
from foodbudget_core.services import MeasurmentUnit


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True, default=None)
    manufacturer = models.CharField(max_length=128)

    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="products")

    # uses either weight or volume
    quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)
    nutrient_unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)
    density = models.FloatField(null=True, blank=True)

    # values below are in (grams) per 100g/100ml

    energy = models.FloatField()  # kcal

    fat = models.FloatField()
    saturated_fat = models.FloatField()
    carbohydrates = models.FloatField()
    sugars = models.FloatField()
    fiber = models.FloatField()
    protein = models.FloatField()
    salt = models.FloatField()

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = {key: str(value) if key == "id" else value for key, value in self.__dict__.items() if not key.startswith("_")}

        return json.dumps(data, indent=4, ensure_ascii=False)
