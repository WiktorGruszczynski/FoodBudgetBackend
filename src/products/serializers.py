from foodbudget_core.services import get_density_by_product_name, is_ean_valid, is_unit_liquid, normalize_ean
from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    density = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "ean",
            "manufacturer",
            "issued_by",
            "recipe",
            "quantity",
            "quantity_unit",
            "nutrient_unit",
            "density",
            "energy_kcal",
            "fat",
            "saturated_fat",
            "carbohydrates",
            "sugars",
            "fiber",
            "protein",
            "salt",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_ean(self, value):
        if not value or not str(value).strip():
            return None

        if not is_ean_valid(normalize_ean(value)):
            raise serializers.ValidationError("Invalid EAN code")

        return value

    def validate(self, data):
        errors = {}
        instance = getattr(self, "instance", None)

        def get_field_value(field_name):
            if field_name in data:
                return data.get(field_name) or 0

            if instance:
                return getattr(instance, field_name) or 0

            return 0

        numeric_fields = [
            "quantity",
            "energy_kcal",
            "fat",
            "saturated_fat",
            "carbohydrates",
            "sugars",
            "fiber",
            "protein",
            "salt",
        ]

        # check negative values
        for field in numeric_fields:
            # check sent fields only
            if get_field_value(field) < 0:
                errors[field] = "Value cannot be negative"

        quantity_unit = data.get("quantity_unit") or (getattr(instance, "quantity_unit") if instance else None)

        if not quantity_unit:
            errors["quantity_unit"] = "Missing quantity unit"

        nutrient_unit = data.get("nutrient_unit") or (getattr(instance, "nutrient_unit") if instance else None)

        if not nutrient_unit:
            errors["nutrient_unit"] = "Missing nutrient unit"

        # check macro nutrients
        # check fat
        fat = get_field_value("fat")
        saturated_fat = get_field_value("saturated_fat")

        if saturated_fat > fat:
            errors["fat"] = errors["saturated_fat"] = "Saturated fat cannot be greater than total fat"

        # check carbs
        carbohydrates = get_field_value("carbohydrates")
        sugars = get_field_value("sugars")

        if sugars > carbohydrates:
            errors["carbohydrates"] = errors["sugars"] = "Sugar content cannot be greater than amount of carbohydrates"

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def _has_recipe(self, instance: Product):
        return instance.recipe is not None

    def create(self, validated_data):
        if is_unit_liquid(validated_data.get("nutrient_unit")):
            validated_data["density"] = get_density_by_product_name(validated_data.get("name"))

        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if self._has_recipe(instance):
            raise serializers.ValidationError({"error": "This product has a recipe assigned to it"})

        fields_to_update = []

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            fields_to_update.append(attr)

        if fields_to_update:
            instance.save(update_fields=fields_to_update)

        return instance
