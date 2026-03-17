import uuid

from django.db import models
from foodbudget_core import settings
from products.models import MeasurmentUnit, Product


class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="recipes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recipe(id={self.id}, name={self.name})"


class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # recipe using this ingredient
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")

    # product used as THIS ingredient
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="usages")

    quantity = models.FloatField()
    unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)

    def __str__(self):
        return f"Ingredient(id={self.id})"
