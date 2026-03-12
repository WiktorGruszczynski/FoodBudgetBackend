from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from products.models import Product, QuantityUnit
from products.services import get_density_by_product_name

# const values below are in grams
NUTRIENTS_LIQUID_LIMIT = 140
NUTRIENTS_SOLID_LIMIT = 100

LIQUID_UNITS = [QuantityUnit.MILLILITER]


class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    name = serializers.CharField(
        max_length=128,
        validators=[UniqueValidator(queryset=Product.objects.all(), message="Product with this name already exists.")],
    )

    ean = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[UniqueValidator(queryset=Product.objects.all(), message="Product with this ean already exists.")],
    )
    manufacturer = serializers.CharField(required=False, max_length=128)

    issued_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, coerce_to_string=False)
    quantity_unit = serializers.ChoiceField(choices=QuantityUnit.choices, required=True)
    nutrient_unit = serializers.ChoiceField(choices=QuantityUnit.choices, required=True)
    density = serializers.DecimalField(max_digits=4, decimal_places=2, required=False, coerce_to_string=False)

    energy = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False)

    fat = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    saturated_fat = serializers.DecimalField(
        max_digits=6, decimal_places=2, coerce_to_string=False, allow_null=True, required=False
    )

    carbohydrates = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    sugars = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False, allow_null=True, required=False)

    fiber = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    protein = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False)
    salt = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=False, allow_null=True, required=False)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_synced_at = serializers.DateTimeField(read_only=True)

    def validate_ean(self, value):
        if value is not None and str(value).strip() == "":
            return None

        if not value:
            return value

        # remove blanks
        value = "".join(value.split())

        if not value.isdigit() or len(value) != 13:
            raise serializers.ValidationError("EAN-13 must consist of exactly 13 digits")

        digits = [int(d) for d in value]
        checksum = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits[:-1]))
        check_digit = (10 - (checksum % 10)) % 10

        if check_digit != digits[-1]:
            raise serializers.ValidationError(f"Invalid EAN checksum. Expected {check_digit} at the end.")

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
            "energy",
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

        # check total amount of nutrients
        total_nutrients = fat + carbohydrates + get_field_value("protein") + get_field_value("fiber") + get_field_value("salt")

        # if liquid, nutrients limit is NUTRIENTS_LIQUID_LIMIT
        # if solid, nutrients the limit is NUTRIENTS_SOLID_LIMIT
        is_liquid = nutrient_unit in LIQUID_UNITS
        nutrients_limit = NUTRIENTS_LIQUID_LIMIT if is_liquid else NUTRIENTS_SOLID_LIMIT

        if total_nutrients > nutrients_limit:
            errors["non_field_errors"] = (
                f"Total nutrients ({total_nutrients}g) exceed the physical limit "
                f"for a 100{nutrient_unit} sample (limit: {nutrients_limit}g)."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def _is_liquid(self, data):
        return data.get("nutrient_unit") in LIQUID_UNITS

    def create(self, validated_data):
        if self._is_liquid(validated_data):
            validated_data["density"] = get_density_by_product_name(validated_data.get("name"))

        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        fields_to_update = []

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            fields_to_update.append(attr)

        if fields_to_update:
            instance.save(update_fields=fields_to_update)

        return instance
