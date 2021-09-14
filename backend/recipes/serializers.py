from django.db import transaction

# from django.http import request
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
    # id = serializers.SlugRelatedField(
    #     # source="ingredient",
    #     slug_field="id",
    #     queryset=Ingredient.objects.all(),
    # )
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
        fields = ["id", "name", "measurement_unit", "amount"]


# class IngredientItemPostSerializer(serializers.ModelSerializer):
#     id = serializers.SlugRelatedField(
#         source="recipe_ingredient",
#         slug_field="id",
#         queryset=Ingredient.objects.all(),
#     )
#     name = serializers.ReadOnlyField(source="ingredient.name")
#     measurement_unit = serializers.ReadOnlyField(
#         source="ingredient.measurement_unit"
#     )

#     class Meta:
#         model = IngredientItem
#         fields = ["id", "name", "measurement_unit", "amount"]


class IngredientItemPostSerializer(serializers.Serializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)


# def validate(self, data):
#     amount = data["amount"]
#     if amount is not int or amount is not float:
#         raise serializers.ValidationError(
#             {
#                 "message": "Укажите количество ингредиента "
#                 "в числовом значении"
#             }
#         )
#     return data


# class IngredientItemPostSerializer(serializers.ModelSerializer):
#     id = serializers.SlugRelatedField(
#         source="ingredients",
#         slug_field="id",
#         queryset=Ingredient.objects.all(),
#     )

#     class Meta:
#         model = IngredientItem
#         fields = [
#             "id",
#             "amount",
#         ]


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
        # print(q)
        # print(IngredientItemSerializer(q, many=True).data)
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
    # ingredients = IngredientItemSerializer(
    #     source="recipe_ingredients", many=True
    # )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            "id",
            "image",
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
        ]

    # def validate(self, data):
    #     ingredients = data["ingredients"]
    #     print(data)
    #     temp_list = []
    #     for ingredient in ingredients:
    #         id = ingredient["id"]
    #         amount = ingredient["amount"]
    #         exist_ingredient = get_object_or_404(
    #             IngredientItem, id=id, amount=amount
    #         )
    #         if exist_ingredient.ingredient in temp_list:
    #             raise serializers.ValidationError(
    #                 {
    #                     "message": "Одинаковых ингредиентов в одном рецепте "
    #                     "быть не может."
    #                 }
    #             )
    #         else:
    #             temp_list.append(exist_ingredient.ingredient)
    #     print(data)
    def validate(self, data):
        unique_ingr = data["ingredients"]
        # print(unique_ingr)
        ingr_list = []
        for item in unique_ingr:
            # print(item)
            id = item["id"]
            # print(id)
            amount = item["amount"]
            try:
                exist_item = get_object_or_404(
                    IngredientItem, id=id, amount=amount
                )
                if exist_item.ingredient in ingr_list:
                    raise serializers.ValidationError(
                        {
                            "message": "Извините,"
                            " но добавить одинаковые ингредиенты нельзя."
                        }
                    )
                else:
                    ingr_list.append(exist_item.ingredient)
            except Exception:
                new_ingr = get_object_or_404(Ingredient, id=id)
                if new_ingr in ingr_list:
                    raise serializers.ValidationError(
                        {
                            "message": "Извините,"
                            " но добавить одинаковые ингредиенты нельзя."
                        }
                    )
                else:
                    ingr_list.append(new_ingr)

        # if len(ingr_list) != len(set(ingr_list)):
        #     raise serializers.ValidationError(
        #         {
        #             "message": "Извините,"
        #             " но добавить одинаковые ингредиенты нельзя."
        #         }
        #     )
        # name = data["name"]
        if self.context["request"].method in ("POST",):
            if Recipe.objects.filter(name=data["name"]):
                # if instanse:
                raise serializers.ValidationError(
                    {"message": "Рецепт с таким названием уже есть!"}
                )
        return data

    # @transaction.atomic
    def create(self, validated_data):
        # q = validated_data
        # print(q)
        request = self.context["request"]
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        # print(ingredients)
        # for ingredient in ingredients:
        #     print(ingredient["id"])
        recipe = Recipe.objects.create(
            author=request.user, image=image, **validated_data
        )
        print(recipe)
        for tag in tags:
            recipe.tags.add(tag)
        items = []
        # for ingredient in ingredients:
        #     id = ingredient["id"]
        #     amount = ingredient["amount"]
        #     item = IngredientItem(
        #         recipe=recipe,
        #         ingredient=get_object_or_404(Ingredient, id=id),
        #         amount=amount,
        #     )
        #     items.append(item)
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
            print(tag)
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
            raise serializers.ValidationError(
                {"message": "У Вас уже есть этот рецепт в избранном."}
            )
        return validated_data
