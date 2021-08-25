from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from users.models import Subscribe

User = get_user_model()


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
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        try:
            request = self.context.get("request")
            subscription = Subscribe.objects.filter(
                subscriber=request.user, author=obj
            )
            return subscription.exists()
        except (TypeError, AttributeError):
            return False
