import uuid

from django.conf import settings
from django.db import models


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True)
    producer = models.CharField(max_length=128)

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

    def __str__(self):
        return f"Product<name={self.name}>"
