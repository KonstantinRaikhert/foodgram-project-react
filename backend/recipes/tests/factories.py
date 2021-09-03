import factory
from faker import Faker
from recipes.models import Ingredient, Tag

fake = Faker(["ru_Ru"])


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ["name"]

    name = factory.Faker(
        "word",
        ext_word_list=["Завтрак", "Обед", "Ужин", "Полдник", "Ланч", "Десерт"],
    )


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ["measurement_unit"]

    name = fake.word()
    measurement_unit = factory.Faker(
        "word", ext_word_list=["кг", "г", "мл", "л"]
    )
