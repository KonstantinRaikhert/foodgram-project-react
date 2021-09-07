from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", method="starts_with")

    class Meta:
        model = Ingredient
        fields = ["name"]

    def starts_with(self, queryset, slug, name):
        return queryset.filter(name__startswith=name)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )

    class Meta:
        model = Recipe
        fields = {"author": ["exact"]}
