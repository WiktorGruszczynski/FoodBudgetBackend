from rest_framework import serializers

from recipes.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()

    class Meta:
        model = Ingredient
        fields = ["id", "product_id", "quantity", "unit"]
        read_only_fields = ["id"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "description", "issued_by", "ingredients", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)

        Ingredient.objects.bulk_create([Ingredient(recipe=recipe, **ingredient) for ingredient in ingredients_data])

        return recipe

    def update(self, instance, validated_data):
        validated_data.pop("issued_by", None)
        ingredients_data = validated_data.pop("ingredients", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if ingredients_data is not None:
            instance.ingredients.all().delete()

            Ingredient.objects.bulk_create([Ingredient(recipe=instance, **ingredient) for ingredient in ingredients_data])

        return instance
