from foodbudget_core.services import is_product_liquid, is_unit_liquid
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
        fields = ["id", "name", "description", "ingredients", "issued_by"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)
        Ingredient.objects.bulk_create([Ingredient(recipe=recipe, **ingredient) for ingredient in ingredients_data])

        recipe.recalculate_product()

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
        instance.recalculate_product()

        return instance
