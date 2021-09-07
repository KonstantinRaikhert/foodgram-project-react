from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
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


class UserChangePasswordSerializer(SetPasswordSerializer):
    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if not is_password_valid:
            raise serializers.ValidationError(
                _("Текущий пароль неверный. Попробуйте снова")
            )
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
