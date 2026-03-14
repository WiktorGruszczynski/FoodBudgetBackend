import pytest
from django.urls import reverse


def create_test_product(
    name="product_name",
    ean: str = None,
    manufacturer="manufacturer",
    quantity=100,
    quantity_unit="g",
    nutrient_unit="g",
    energy=100,
    fat=0.0,
    saturated_fat=0.0,
    carbohydrates=0.0,
    sugars=0.0,
    fiber=0.0,
    protein=0.0,
    salt=0.0,
):
    return {
        "name": name,
        "ean": ean,
        "manufacturer": manufacturer,
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "nutrient_unit": nutrient_unit,
        "energy": energy,
        "fat": fat,
        "saturated_fat": saturated_fat,
        "carbohydrates": carbohydrates,
        "sugars": sugars,
        "fiber": fiber,
        "protein": protein,
        "salt": salt,
    }


@pytest.mark.django_db
class TestProductAPI:
    url = reverse("product-list")

    def test_create_product(self, api_client, authenticated_user):
        "Check if correct json results in creating new product and 201 status code"

        data = create_test_product(
            name="Czekolada Mleczna",
            manufacturer="Goplana",
            quantity=100,
            quantity_unit="g",
            energy=100,
            fat=45,
            saturated_fat=25,
            carbohydrates=15,
            sugars=10,
            fiber=10,
            protein=10,
            salt=0.05,
        )

        response = api_client.post(self.url, data, format="json")

        # is status code correct
        assert response.status_code == 201

        # is product data present
        assert response.data["id"] is not None

    def test_macro_exceed_limit_fails(self, api_client, authenticated_user):
        "Check if macro validation works (sum of macros cannot be grater than specified limit)"

        data = create_test_product(fat=50, carbohydrates=60)

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 400

        assert "non_field_errors" in response.data

    def test_fat_content_validation(self, api_client, authenticated_user):
        "Check if total fat >= saturated_fat"

        too_much_saturated_fat = create_test_product(fat=90, saturated_fat=95)

        response = api_client.post(self.url, too_much_saturated_fat, format="json")

        assert response.status_code == 400

        assert "fat" in response.data
        assert "saturated_fat" in response.data

    def test_carbohydrates_content_validation(self, api_client, authenticated_user):
        "Check if total carbohydrates >= sugars"

        test_product = create_test_product(carbohydrates=90, sugars=100)

        response = api_client.post(self.url, test_product, format="json")

        assert response.status_code == 400

        assert "sugars" in response.data
        assert "carbohydrates" in response.data

    def test_nutrients_equality_success(self, api_client, authenticated_user):
        """Check if subproduct content is equal to product content"""
        data = create_test_product(carbohydrates=50, sugars=50, fat=10, saturated_fat=10)
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 201

    def test_limit_adjust_for_liquids(self, api_client, authenticated_user):
        """Nutrients limit for liquids is higher"""

        data = create_test_product(nutrient_unit="ml", carbohydrates=90, fat=40, protein=3.5, fiber=0.5, salt=1)

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == 201

    def test_invalid_quantity_unit(self, api_client, authenticated_user):
        data = create_test_product(quantity_unit="cm^3")

        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 400
        assert "quantity_unit" in response.data

    def test_negative_components_addup_to_positive(self, api_client, authenticated_user):
        data = create_test_product(fat=150, protein=-100)

        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 400
