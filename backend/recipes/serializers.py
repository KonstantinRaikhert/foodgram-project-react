from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientItem,
    Recipe,
    Tag,
)
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
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientItem
        fields = ["name", "measurement_unit", "amount"]


class IngredientItemPostSerializer(serializers.Serializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    def validate(self, data):
        amount = data["amount"]
        if amount is not int or amount is not float:
            raise serializers.ValidationError(
                {
                    "message": "Укажите количество ингредиента "
                    "в числовом значении"
                }
            )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        q = IngredientItem.objects.filter(recipe=obj)
        return IngredientItemSerializer(q, many=True).data

    def get_is_favorited(self, obj):
        try:
            request = self.context.get("request")
            is_favorited = FavoriteRecipe.objects.filter(
                user=request.user, recipe_id=obj.id
            )
            return is_favorited.exists()
        except TypeError:
            return False


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientItemPostSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            "image",
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
        ]

    def validate(self, data):
        ingredients = data["ingredients"]
        temp_list = []
        for ingredient in ingredients:
            id = ingredient["id"]
            amount = ingredient["amount"]
            exist_ingredient = get_object_or_404(
                IngredientItem, id=id, amount=amount
            )
            if exist_ingredient in temp_list:
                raise serializers.ValidationError(
                    {
                        "message": "Одинаковых ингредиентов в одном рецепте "
                        "быть не может."
                    }
                )
            else:
                temp_list.append(exist_ingredient)
        return data

    @transaction.atomic
    def created(self, validated_data):
        request = self.context["request"]
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=request.user, image=image, **validated_data
        )
        for tag in tags:
            recipe.tags.add(tag)
        items = [
            IngredientItem(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient["id"],
                    amount=ingredient["amount"],
                ),
            )
            for ingredient in ingredients
        ]
        IngredientItem.objects.bulk_create(items)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        try:
            image = validated_data.pop("image")
            instance.image = image
            instance.save()
        except KeyError:
            pass

        recipe = Recipe.objects.filter(id=instance.id)
        recipe.update(**validated_data)

        instance_tags = [tag for tag in instance.tags.all()]
        for tag in tags:
            if tag in instance_tags:
                instance_tags.remove(tag)
            else:
                instance_tags.add(tag)
        instance_tags.remove(*instance_tags)

        instance_ingredients = [
            ingredient for ingredient in instance.ingredients.all()
        ]
        for item in ingredients:
            amount = item["amount"]
            id = item["id"]
            try:
                exists_item_ingredient = IngredientItem.objects.get(
                    id=id, amount=amount
                )
                instance.ingredients.remove(exists_item_ingredient.ingredient)
            except IngredientItem.DoesNotExist:
                IngredientItem.objects.create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=id),
                    amount=amount,
                )

        instance.ingredients.remove(*instance_ingredients)

        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        obj, created = FavoriteRecipe.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not created:
            raise serializers.ValidationError(
                {"message": "У Вас уже есть этот рецепт в избранном."}
            )
        return validated_data
