import random
import urllib

import factory
from django.core.files.base import ContentFile
from faker import Faker
from recipes.models import Ingredient, IngredientItem, Recipe, Tag
from users.models import CustomUser

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


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    author = factory.Iterator(CustomUser.objects.all())

    name = factory.Faker("word")
    text = factory.Faker("text")
    cooking_time = factory.LazyFunction(lambda: random.randint(10, 100))

    @factory.post_generation
    def tags(self, created, extracted, **kwargs):
        if not created:
            return

        at_least = 1
        how_many = extracted or at_least
        tags_count = Tag.objects.count()
        how_many = min(tags_count, how_many)

        tags = Tag.objects.order_by("?")[:how_many]
        self.tags.add(*tags)

    @factory.post_generation
    def ingredients(self, created, extracted, **kwargs):
        if not created:
            return

        at_least = 4
        how_many = extracted or at_least

        ingredients_count = Ingredient.objects.count()
        start = random.randint(1, ingredients_count)
        how_many = min(ingredients_count, how_many) + start

        ingredients = Ingredient.objects.order_by("?")[start:how_many]
        [
            IngredientItem.objects.create(
                ingredient=ingredient,
                recipe=self,
                amount=random.randint(1, 500),
            )
            for ingredient in ingredients
        ]
        self.ingredients.add(*ingredients)

    @factory.post_generation
    def image(self, created, extracted, **kwargs):
        if not created:
            return

        image = urllib.request.urlopen("https://picsum.photos/800/800").read()
        self.image.save(self.name + ".jpg", ContentFile(image), save=False)
