from products.serializers import ProductSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # w response - obiekt
    product_id = serializers.UUIDField(write_only=True)  # w request - UUID

    class Meta:
        model = Ingredient
        fields = ["id", "product", "product_id", "quantity", "unit"]
        read_only_fields = ["id"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "description", "issued_by", "ingredients", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
