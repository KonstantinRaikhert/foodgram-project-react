from django.urls import reverse
from recipes.tests.factories import (
    IngredientFactory,
    RecipeFactory,
    TagFactory,
)
from rest_framework.test import APIClient, APITestCase
from users.tests.factories import UserFactory


class UrlUsersTests(APITestCase):
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
        clinet = UrlUsersTests.unauthorized_client

        response = clinet.get(reverse("users-list"))
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("users-list") + "1/")
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("users-list") + "subscriptions/")
        self.assertEqual(response.status_code, 401)

        response = clinet.get(reverse("users-list") + "me/")
        self.assertEqual(response.status_code, 401)
