from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from recipes.models import Ingredient

from products.models import Product


@receiver(post_save, sender=Product)
def on_product_updated(sender, instance, **kwargs):
    """
    When product is saved, find all recipes, that use it and force recalculation
    """

    def do_recalculation():
        instance.refresh_from_db()

        # find ingredients using this product
        affected_ingredients = Ingredient.objects.filter(product=instance).select_related("recipe")

        # create set of recipes to update
        recipes_to_update = {ingredient.recipe for ingredient in affected_ingredients}

        for recipe in recipes_to_update:
            # instance.recipe_id - product is made by recipe with this ID
            # recipe.id - ID of recipe, which uses this Product as Ingredient
            if instance.recipe_id != recipe.id:
                recipe.recalculate_product()

    transaction.on_commit(do_recalculation)

    print("\n\n")
