import factory
from faker import Faker
from recipes.models import Ingredient, Tag

fake = Faker(["ru_Ru"])


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ["name"]

    name = fake.word()


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ["name"]

    name = fake.word()
    measurement_unit = fake.word()
