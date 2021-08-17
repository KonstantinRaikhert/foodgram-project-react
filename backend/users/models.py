from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(
            username, email, password=password, **extra_fields
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255, unique=True, verbose_name="Электронная почта"
    )
    username = models.CharField(
        max_length=255, unique=True, verbose_name="Имя пользователя"
    )
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    is_active = models.BooleanField(
        default=True, verbose_name="Статус активности"
    )
    is_staff = models.BooleanField(
        default=False, verbose_name="Статус администратора"
    )
    is_superuser = models.BooleanField(
        default=False, verbose_name="Статус суперпользователя"
    )
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name="Дата регистрации"
    )
    last_login = models.DateTimeField(
        null=True, verbose_name="Последнее посещение"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def get_full_name(self):
        return f"{self.first_name} - {self.last_name}"

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["id"]
        constraints = [
            UniqueConstraint(
                fields=["author", "subscriber"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return self.author.username
