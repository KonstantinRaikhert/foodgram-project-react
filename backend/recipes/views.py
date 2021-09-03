from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import RecipeFilter
from recipes.models import Ingredient, Recipe, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("id")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    serializer_class = RecipeSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by("-id")
        return queryset
