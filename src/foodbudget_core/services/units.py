from django.db import models


class MeasurmentUnit(models.TextChoices):
    GRAM = "g"
    MILLILITER = "ml"


def is_unit_liquid(unit_value: str):
    return unit_value == MeasurmentUnit.MILLILITER
