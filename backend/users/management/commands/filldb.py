import csv
from random import randint

import factory
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Recipe, Tag
from recipes.tests.factories import (
    IngredientFactory,
    RecipeFactory,
    TagFactory,
)
from users.tests.factories import SubscribeFactory, UserFactory


class AllFactories:
    def create_users_default(self, arg):
        UserFactory.create_batch(arg)

    def create_users_is_staff(self, arg):
        for _ in range(arg):
            UserFactory.create(is_staff=True)

    def create_users_no_active(self, arg):
        for _ in range(arg):
            UserFactory._create(is_active=False)

    def create_subscribers(self, arg):
        SubscribeFactory.create_batch(arg)

    def create_tags(self, arg):
        TagFactory.create_batch(arg)

    def create_ingredients(self, arg):
        IngredientFactory.create_batch(arg)

    def create_recipe(self, arg):
        for _ in range(arg):
            num_tags = randint(1, 3)
            num_ingredients = randint(3, 10)
            RecipeFactory.create(tags=num_tags, ingredients=num_ingredients)


all_factories = AllFactories()

OPTIONS_AND_FUNCTIONS = {
    "users_default": all_factories.create_users_default,
    "users_admin": all_factories.create_users_is_staff,
    "users_no_active": all_factories.create_users_no_active,
    "subscriber": all_factories.create_subscribers,
    "tag": all_factories.create_tags,
    "ingredient": all_factories.create_ingredients,
    "recipe": all_factories.create_recipe,
}

MEALTIME_TAGS = ["Завтрак", "Обед", "Ужин"]


class MyException(Exception):
    pass


class Command(BaseCommand):
    help = "Fill Data Base with the test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users_default",
            nargs=1,
            type=int,
            help="Creates Users default objects",
            required=False,
        )
        parser.add_argument(
            "--users_admin",
            nargs=1,
            type=int,
            help="Creates Users objects witn staff permissions",
            required=False,
        )
        parser.add_argument(
            "--users_no_active",
            nargs=1,
            type=int,
            help="Creates not active Users objects",
            required=False,
        )
        parser.add_argument(
            "--subscriber",
            nargs=1,
            type=int,
            help="Creates Subscriber objects for each user",
            required=False,
        )
        parser.add_argument(
            "--tag",
            nargs=1,
            type=int,
            help="Creates Tag objects",
            required=False,
        )
        parser.add_argument(
            "--ingredient",
            nargs=1,
            type=int,
            help="Creates Ingredient objects",
            required=False,
        )
        parser.add_argument(
            "--recipe",
            nargs=1,
            type=int,
            help="Creates Recipe objects",
            required=False,
        )

    def handle(self, *args, **options):  # noqa

        optional_arguments = 0
        for item in list(OPTIONS_AND_FUNCTIONS):
            if options[item]:
                optional_arguments += 1
                with factory.Faker.override_default_locale("ru_RU"):
                    OPTIONS_AND_FUNCTIONS[item](options[item][0])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{options[item][0]} {item} created successfully"
                        )
                    )

        if optional_arguments == 0:
            try:
                with factory.Faker.override_default_locale("ru_RU"):
                    if Recipe.objects.count() > 10:
                        raise MyException()
                    UserFactory.create_batch(5)
                    for _ in range(5):
                        UserFactory.create(is_staff=True)
                    for _ in range(5):
                        UserFactory.create(is_active=False)
                    SubscribeFactory.create_batch(30)
                    for tag in range(len(MEALTIME_TAGS)):
                        TagFactory.create(
                            name=MEALTIME_TAGS[tag],
                            color=Tag.Color.choices[tag][0],
                        )
                    with open("data/ingredients.csv", "r") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            _, created = Ingredient.objects.get_or_create(
                                name=row[0], measurement_unit=row[1]
                            )
                    for _ in range(20):
                        num_tags = randint(1, 3)
                        num_ingredients = randint(3, 10)
                        RecipeFactory.create(
                            tags=num_tags, ingredients=num_ingredients
                        )

                    self.stdout.write(
                        self.style.SUCCESS(
                            "The database is filled with test data"
                        )
                    )
            except MyException:
                self.stdout.write(
                    self.style.ERROR(
                        "The database is already filled with standard test "
                        "data. To top up individual tables, use the arguments."
                    )
                )
