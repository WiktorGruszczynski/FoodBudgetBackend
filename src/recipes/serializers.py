from foodbudget_core.services import DensityPreset, MeasurmentUnit, is_unit_liquid
from rest_framework import serializers

from recipes.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    subrecipe_id = serializers.UUIDField(required=False, allow_null=True, default=None)

    class Meta:
        model = Ingredient
        fields = ["id", "product_id", "subrecipe_id", "quantity", "unit"]
        read_only_fields = ["id"]

    def validate(self, data):
        product_id = data.get("product_id")
        subrecipe_id = data.get("subrecipe_id")

        if bool(product_id) == bool(subrecipe_id):
            raise serializers.ValidationError("provide either product_id or subrecipe_id")

        return data

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class RecipeSerializer(serializers.ModelSerializer):
    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientSerializer(many=True)  # many=True -> list of ingredients
    total_nutrients = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    quantity_unit = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "description",
            "issued_by",
            "quantity",
            "quantity_unit",
            "total_nutrients",
            "ingredients",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_quantity_unit(self, obj):
        return MeasurmentUnit.GRAM

    # in response quantity is generated dynamically
    # it serves as one source of truth
    # even after modyfing ingredient list,
    def get_quantity(self, obj):
        def callback(ingredient):
            if ingredient.product_id is not None and is_unit_liquid(ingredient.unit) and ingredient.product.density:
                return ingredient.product.density * ingredient.quantity

            return ingredient.quantity

        return sum(callback(ingredient) for ingredient in obj.ingredients.select_related("product").all())

    def get_total_nutrients(self, obj):
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

        for ingredient in obj.ingredients.select_related("product", "subrecipe").all():
            if ingredient.product:
                source_nutrients = {key: getattr(ingredient.product, key) for key in totals}
                factor = ingredient.quantity / 100

                # if the nutrient unit is liquid and ingredient unit is in liquid
                # EXAMPLE
                # Product(Soy sauce, nutrients per 100ml)
                # Ingredient(Product, quantity in 'ml' units)
                if is_unit_liquid(ingredient.product.nutrient_unit) and is_unit_liquid(ingredient.unit):
                    factor *= ingredient.product.density or DensityPreset.STANDARD

            elif ingredient.subrecipe:
                source_nutrients = self.get_total_nutrients(ingredient.subrecipe)
                factor = (100 / self.get_quantity(ingredient.subrecipe)) * (ingredient.quantity / 100)

            else:
                continue

            for key in totals:
                totals[key] += source_nutrients[key] * factor

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
