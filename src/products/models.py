import json
import uuid

from django.conf import settings
from django.db import models


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True, default=None)
    manufacturer = models.CharField(max_length=128)

    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")

    # uses either weight or volume
    weight = models.IntegerField(null=True, blank=True)
    volume = models.IntegerField(null=True, blank=True)

    # values below are in (grams) per 100g/100ml

    energy = models.FloatField()  # kcal

    fat = models.FloatField()
    saturated_fat = models.FloatField()
    carbohydrates = models.FloatField()
    sugars = models.FloatField()
    fiber = models.FloatField()
    protein = models.FloatField()
    salt = models.FloatField()

    # Automatycznie ustawia datę tylko raz, przy utworzeniu obiektu
    created_at = models.DateTimeField(auto_now_add=True)

    # Automatycznie aktualizuje datę przy każdym wywołaniu .save()
    updated_at = models.DateTimeField(auto_now=True)

    # Pole, które dodaliśmy wcześniej - sterowane ręcznie w funkcji scan
    last_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        data = {key: str(value) if key == "id" else value for key, value in self.__dict__.items() if not key.startswith("_")}

        return json.dumps(data, indent=4, ensure_ascii=False)
