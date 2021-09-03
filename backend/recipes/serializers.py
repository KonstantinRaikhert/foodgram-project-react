from recipes.models import Ingredient, IngredientItem, Recipe, Tag
from rest_framework import serializers
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientItemSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="ingredient.item")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientItem
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        queryset = IngredientItem.objects.filter(recipe=obj)
        return IngredientItemSerializer(queryset, many=True).data
