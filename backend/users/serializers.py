from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from recipes.models import Recipe
from rest_framework import serializers
from users.models import Subscribe

User = get_user_model()

CURRENT_PASSWORD_ERROR = serializers.ValidationError(
    _("Текущий пароль неверный. Попробуйте снова")
)
SUBSCRIBE_YOURSELF_ERROR = serializers.ValidationError(
    {"message": "Подписка на самого себя невозможна!"}
)
SAME_SUBSCRIBE_ERROR = serializers.ValidationError(
    {"message": "Вы уже подписаны на этого автора!"}
)


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        subscription = Subscribe.objects.filter(
            subscriber=request.user, author=obj
        ).exists()
        return subscription


class UserChangePasswordSerializer(SetPasswordSerializer):
    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if not is_password_valid:
            raise CURRENT_PASSWORD_ERROR
        return value

    def validate(self, data):
        password_validation.validate_password(
            data["new_password"], self.context["request"].user
        )
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = "__all__"

    def create(self, validated_data):
        author = validated_data["author"]
        subscriber = validated_data["subscriber"]
        if author == subscriber:
            raise SUBSCRIBE_YOURSELF_ERROR
        _, created = Subscribe.objects.get_or_create(
            author=author, subscriber=subscriber
        )
        if not created:
            raise SAME_SUBSCRIBE_ERROR
        return validated_data


class AuthorSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):

        request = self.context["request"]
        recipes_limit = request.query_params.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj)

        if recipes_limit is not None and recipes_limit.isnumeric():
            recipes_limit = int(recipes_limit)
            queryset = queryset[:recipes_limit]

        return [RecipeSubscribeSerializer(query).data for query in queryset]

    def get_recipes_count(self, obj):
        qset = Recipe.objects.filter(author=obj)
        return qset.count()
