from recipes.models import Ingredient, Tag
from recipes.serializers import IngredientSerializer, TagSerializer
from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("id")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
