import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipes.models import Recipe

User = get_user_model()


def create_test_recipe(name="Test Recipe", description="Test description"):
    return {
        "name": name,
        "description": description,
        "ingredients": [],
    }


@pytest.mark.django_db
class TestRecipeAPI:
    url = reverse("recipe-list")

    def test_delete_other_user_recipe_fails(self, api_client, authenticated_user):
        "Check if user cannot delete recipe created by another user"

        other_user = User.objects.create_user(email="other@mail.com", password="password67")
        recipe = Recipe.objects.create(name="Other Recipe", description="desc", issued_by=other_user)

        url = reverse("recipe-detail", kwargs={"pk": recipe.id})
        response = api_client.delete(url)

        assert response.status_code == 403
