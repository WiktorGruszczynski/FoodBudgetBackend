from django.db import models


class MeasurmentUnit(models.TextChoices):
    GRAM = "g"
    MILLILITER = "ml"


def is_unit_liquid(unit_value: str):
    return unit_value == MeasurmentUnit.MILLILITER


def is_product_liquid(product):
    return is_unit_liquid(product.quantity_unit) or is_unit_liquid(product.nutrient_unit)
