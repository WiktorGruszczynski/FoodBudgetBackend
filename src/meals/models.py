import uuid

from django.conf import settings
from django.db import models
from products.models import Product
from recipes.models import Recipe


class MealType(models.TextChoices):
    BREAKFAST = ("breakfast",)
    LUNCH = ("lunch",)
    DINNER = ("dinner",)
    SNACK_1 = ("snack_1",)
    SNACK_2 = ("snack_2",)
    SNACK_3 = "snack_3"


class Meal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meals")
    date = models.DateField()
    meal_type = models.CharField(max_length=16, choices=MealType.choices)

    def __str__(self):
        return f"Meal(id={self.id}, type={self.meal_type}, date={self.date})"


class MealItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items")
    recipe = models.ForeignKey(Recipe, null=True, blank=True, on_delete=models.CASCADE, related_name="meal_items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE, related_name="meal_items")
    portion = models.FloatField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="meal_item_recipe_or_product",
                condition=(
                    models.Q(recipe__isnull=False, product__isnull=True) | models.Q(recipe__isnull=True, product__isnull=False)
                ),
            )
        ]

    def __str__(self):
        source = self.recipe_id or self.product_id
        return f"MealItem(id={self.id}, source={source}, portion={self.portion}g)"
