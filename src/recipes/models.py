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

    # only product or subrecipe allowed exclusivly
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE, related_name="usages"
    )  # product used as THIS ingredient
    subrecipe = models.ForeignKey(
        Recipe, null=True, blank=True, on_delete=models.CASCADE, related_name="used_in"
    )  # product(made from recipe) used as THIS ingredient

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")  # recipe using this ingredient
    quantity = models.FloatField()
    unit = models.CharField(max_length=8, choices=MeasurmentUnit.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="ingredient_product_or_subrecipe",
                condition=(
                    models.Q(product__isnull=False, subrecipe__isnull=True)
                    | models.Q(product__isnull=True, subrecipe__isnull=False)
                ),
            )
        ]

    def __str__(self):
        source_type = "product" if self.product_id is not None else "recipe"

        return f"Ingredient(id={self.id}, source={self.product_id or self.subrecipe_id}, source_type={source_type})"
