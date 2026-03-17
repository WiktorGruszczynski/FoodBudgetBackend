from foodbudget_core.services import DensityPreset, MeasurmentUnit, is_product_liquid, is_unit_liquid
from products.models import Product
from rest_framework import serializers

from recipes.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "product", "quantity", "unit"]
        read_only_fields = ["id"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        product = data.get("product")
        ingredient_unit = data.get("unit")

        # Prevent usage of liquid units for non-liquid products
        if not is_product_liquid(product) and is_unit_liquid(ingredient_unit):
            raise serializers.ValidationError({"unit": "Wrong unit"})

        # Allow to use unit of mass if product has defined density
        if is_product_liquid(product) and not is_unit_liquid(ingredient_unit) and not product.density:
            raise serializers.ValidationError({"unit": "Wrong unit"})

        return data


class RecipeSerializer(serializers.ModelSerializer):
    """
    Creating new Recipe object also creates new Product.
    Generally Recipe object is just a description with a list of ingredients.
    """

    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientSerializer(many=True)  # many=True -> list of ingredients

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def _get_ingredient_density(self, ingredient):
        if is_unit_liquid(ingredient.unit) and ingredient.product.density:
            return ingredient.product.density

        return DensityPreset.STANDARD

    def _make_product_from_recipe(self, recipe: Recipe):
        total_mass = 0.0
        nutrients = {
            key: 0.0 for key in ["energy_kcal", "fat", "saturated_fat", "carbohydrates", "sugars", "protein", "fiber", "salt"]
        }

        for ingredient in recipe.ingredients.select_related("product").all():
            product = ingredient.product
            density = product.density or DensityPreset.STANDARD

            if is_unit_liquid(ingredient.unit):
                ingredient_mass = ingredient.quantity * density
                ingredient_volume = ingredient.quantity
            else:
                ingredient_mass = ingredient.quantity
                ingredient_volume = ingredient.quantity / density

            total_mass += ingredient_mass

            factor = ingredient_volume / 100.0 if is_unit_liquid(product.nutrient_unit) else ingredient_mass / 100.0

            for nutrient_name in nutrients:
                val_per_100 = getattr(product, nutrient_name) or 0
                nutrients[nutrient_name] += float(val_per_100) * factor

        if total_mass == 0:
            raise serializers.ValidationError("Invalid ingredients")

        product_data = {
            "quantity": round(total_mass, 2),
            "quantity_unit": MeasurmentUnit.GRAM,
            "nutrient_unit": MeasurmentUnit.GRAM,
            "name": recipe.name,
        }

        for nutrient_name in nutrients:
            product_data[nutrient_name] = round((nutrients[nutrient_name] / total_mass) * 100, 2)

        product, created = Product.objects.update_or_create(recipe=recipe, defaults=product_data)

        return product

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)
        Ingredient.objects.bulk_create([Ingredient(recipe=recipe, **ingredient) for ingredient in ingredients_data])

        self._make_product_from_recipe(recipe)

        return recipe

    def update(self, instance, validated_data):
        validated_data.pop("issued_by", None)
        ingredients_data = validated_data.pop("ingredients", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            Ingredient.objects.bulk_create([Ingredient(recipe=instance, **ingredient) for ingredient in ingredients_data])

        instance.save()

        self._make_product_from_recipe(instance)

        return instance
