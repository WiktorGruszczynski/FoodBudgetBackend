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
    nutrients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "description", "issued_by", "ingredients", "created_at", "updated_at", "nutrients"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_nutrients(self, obj):
        totals = {
            "energy": 0,
            "fat": 0,
            "saturated_fat": 0,
            "carbohydrates": 0,
            "sugars": 0,
            "fiber": 0,
            "protein": 0,
            "salt": 0,
        }

        for ingredient in obj.ingredients.select_related("product").all():
            factor = ingredient.quantity / 100

            for key in totals:
                totals[key] += getattr(ingredient.product, key) * factor

        for key in totals:
            totals[key] = round(totals[key], 2)

        return totals

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
