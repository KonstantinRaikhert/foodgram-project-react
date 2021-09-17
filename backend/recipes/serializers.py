from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientItem,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from users.serializers import UserSerializer

SAME_INGREDIENTS_ERROR = serializers.ValidationError(
    {"message": "Одинаковых ингредиентов в одном рецепте быть не может."}
)
INGREDIENT_AMOUNT_ERROR = serializers.ValidationError(
    {"message": "Введите количество ингредиентов в целочисленном формате"}
)
SAME_RECIPE_ERROR = serializers.ValidationError(
    {"message": "Рецепт с таким названием уже есть!"}
)
SAME_RECIPE_IN_FAVORITE_ERROR = serializers.ValidationError(
    {"message": "У Вас уже есть этот рецепт в избранном."}
)
SAME_RECIPE_IN_SHOPPINGCART_ERROR = serializers.ValidationError(
    {"message": "У Вас уже есть этот рецепт в корзине покупок."}
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientItemSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="name",
        read_only=True,
    )
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientItem
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientItemPostSerializer(serializers.Serializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.CharField(write_only=True)

    def validate(self, data):
        amount = data["amount"]
        if not amount.isnumeric():
            raise INGREDIENT_AMOUNT_ERROR
        return data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        q_set = IngredientItem.objects.filter(recipe=obj)
        return IngredientItemSerializer(q_set, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        is_favorited = FavoriteRecipe.objects.filter(
            user=request.user, recipe_id=obj.id
        ).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        is_in_cart = ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()
        return is_in_cart


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientItemPostSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "image",
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        unique_ingr = data["ingredients"]
        ingr_list = []
        for item in unique_ingr:
            id = item["id"]
            amount = item["amount"]
            try:
                exist_item = get_object_or_404(
                    IngredientItem, id=id, amount=amount
                )
                if exist_item.ingredient in ingr_list:
                    raise SAME_INGREDIENTS_ERROR
                else:
                    ingr_list.append(exist_item.ingredient)
            except Exception:
                new_ingr = get_object_or_404(Ingredient, id=id)
                if new_ingr in ingr_list:
                    raise SAME_INGREDIENTS_ERROR
                else:
                    ingr_list.append(new_ingr)

        if self.context["request"].method in ("POST",):
            if Recipe.objects.filter(name=data["name"]):
                raise SAME_RECIPE_ERROR
        return data

    @transaction.atomic
    def create(self, validated_data):
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
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"],
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
                instance.tags.add(tag)
        instance.tags.remove(*instance_tags)
        instance_ingredients = [
            ingredient for ingredient in instance.ingredients.all()
        ]
        for item in ingredients:
            try:
                id = item["id"]
                exists_item_ingredient = IngredientItem.objects.get(
                    ingredient_id=id, recipe=instance
                )
                instance.ingredients.remove(exists_item_ingredient.ingredient)
            except IngredientItem.DoesNotExist:
                amount = item["amount"]
                IngredientItem.objects.create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=id),
                    amount=amount,
                )
        if instance_ingredients:
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
            raise SAME_RECIPE_IN_FAVORITE_ERROR
        return validated_data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        _, created = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not created:
            raise SAME_RECIPE_IN_SHOPPINGCART_ERROR
        return validated_data
