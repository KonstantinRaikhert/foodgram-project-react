import factory
from recipes.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ["name"]

    name = "Tag"
