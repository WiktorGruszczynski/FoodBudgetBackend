import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from foodbudget_core import settings
from foodbudget_core.services import DensityPreset, MeasurmentUnit, is_unit_liquid
from products.models import Product


class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="recipes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recipe(id={self.id}, name={self.name})"

    def recalculate_product(self):
        """
        Oblicza makroskładniki i aktualizuje powiązany obiekt Product.
        """
        from products.models import Product  # Import wewnątrz, aby uniknąć pętli importów

        total_mass = 0.0
        nutrients = {
            key: 0.0 for key in ["energy_kcal", "fat", "saturated_fat", "carbohydrates", "sugars", "protein", "fiber", "salt"]
        }

        # Pobieramy składniki korzystając z related_name="ingredients"
        ingredients = self.ingredients.select_related("product").all()

        for ingredient in ingredients:
            product = ingredient.product
            density = product.density or DensityPreset.STANDARD

            if is_unit_liquid(ingredient.unit):
                ingredient_mass = ingredient.quantity * density
                ingredient_volume = ingredient.quantity
            else:
                ingredient_mass = ingredient.quantity
                ingredient_volume = ingredient.quantity / density

            total_mass += ingredient_mass

            # Sprawdzamy jednostkę miary nutrient_unit w produkcie-składniku
            factor = ingredient_volume / 100.0 if is_unit_liquid(product.nutrient_unit) else ingredient_mass / 100.0

            for nutrient_name in nutrients:
                val_per_100 = getattr(product, nutrient_name) or 0
                nutrients[nutrient_name] += float(val_per_100) * factor

        if total_mass == 0:
            raise ValidationError("Total mass of recipe ingredients cannot be 0.")

        product_data = {
            "quantity": round(total_mass, 2),
            "quantity_unit": MeasurmentUnit.GRAM,
            "nutrient_unit": MeasurmentUnit.GRAM,
            "name": self.name,
            "issued_by": self.issued_by,
        }

        for nutrient_name in nutrients:
            product_data[nutrient_name] = round((nutrients[nutrient_name] / total_mass) * 100, 2)

        with transaction.atomic():
            product, created = Product.objects.update_or_create(recipe=self, defaults=product_data)

        return product


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
