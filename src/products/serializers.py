from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from products.models import Product

# const values below are in grams
NUTRIENTS_LIQUID_LIMIT = 150
NUTRIENTS_SOLID_LIMIT = 100


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

    weight = serializers.IntegerField(required=False, allow_null=True)
    volume = serializers.IntegerField(required=False, allow_null=True)

    energy = serializers.FloatField()

    fat = serializers.FloatField()
    saturated_fat = serializers.FloatField()

    carbohydrates = serializers.FloatField()
    sugars = serializers.FloatField()

    fiber = serializers.FloatField()
    protein = serializers.FloatField()
    salt = serializers.FloatField()

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
        numeric_fields = [
            "weight",
            "volume",
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
            if (data.get(field) or 0) < 0:
                errors[field] = "Value cannot be negative"

        # check weight and volume
        weight = data.get("weight") or 0
        volume = data.get("volume") or 0

        # both null
        if not weight and not volume:
            errors["weight"] = errors["volume"] = "Provide weight or volume"

        # both not null
        if weight and volume:
            errors["weight"] = errors["volume"] = "Cannot provide both weight and volume. Choose one"

        # check macro nutrients
        # check fat
        fat = data.get("fat") or 0
        saturated_fat = data.get("saturated_fat") or 0

        if saturated_fat > fat:
            errors["fat"] = errors["saturated_fat"] = "Saturated fat cannot be greater than total fat"

        # check carbs
        carbohydrates = data.get("carbohydrates") or 0
        sugars = data.get("sugars") or 0

        if sugars > carbohydrates:
            errors["carbohydrates"] = errors["sugars"] = "Sugar content cannot be greater than amount of carbohydrates"

        # check total amount of nutrients
        total_nutrients = fat + carbohydrates + (data.get("protein") or 0) + (data.get("fiber") or 0) + (data.get("salt") or 0)

        # if liquid, nutrients limit is NUTRIENTS_LIQUID_LIMIT
        # if solid, nutrients the limit is NUTRIENTS_SOLID_LIMIT
        nutrients_limit = NUTRIENTS_LIQUID_LIMIT if volume > 0 else NUTRIENTS_SOLID_LIMIT

        if total_nutrients > nutrients_limit:
            errors["non_field_errors"] = (
                f"Total nutrients ({total_nutrients}g) exceed the physical limit "
                f"for a 100{'ml' if volume > 0 else 'g'} sample (limit: {nutrients_limit}g)."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        return Product.objects.create(**validated_data)
