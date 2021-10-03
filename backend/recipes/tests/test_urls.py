from django.urls import reverse
from recipes.tests.factories import (
    IngredientFactory,
    RecipeFactory,
    TagFactory,
)
from rest_framework.test import APIClient, APITestCase
from users.tests.factories import UserFactory


class UrlRecipeTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        UserFactory.create_batch(5)
        IngredientFactory.create_batch(10)
        TagFactory.create_batch(2)
        RecipeFactory.create_batch(2)

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_recipes = reverse("recipes-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_urls_smoke_unauthorized(self):
        client = UrlRecipeTests.unauthorized_client

        response = client.get(reverse("recipes-list"))
        self.assertEqual(response.status_code, 200)

        response = client.get(reverse("recipes-list") + "1/")
        self.assertEqual(response.status_code, 200)

        response = client.get(reverse("ingredients-list"))
        self.assertEqual(response.status_code, 200)

        response = client.get(reverse("ingredients-list") + "1/")
        self.assertEqual(response.status_code, 200)
