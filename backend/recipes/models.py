from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy
from users.models import CustomUser
from utilites.utils import slugify


class Tag(models.Model):
    class Color(models.TextChoices):
        ORANGE = "#E26C2D", gettext_lazy("Оранжевый")
        GREEN = "#49B64E", gettext_lazy("Зелёный")
        PURPLE = "#8775D2", gettext_lazy("Фиолетовый")

    name = models.CharField(max_length=50, unique=True, blank=False)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(
        verbose_name="Цвет тега", max_length=8, choices=Color.choices
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название", max_length=200, blank=False
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=10,
        blank=False,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Автор"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientItem",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    name = models.CharField(max_length=200, verbose_name="Название")
    image = models.ImageField(upload_to="recipes/", verbose_name="Изображение")
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class IngredientItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        ordering = ["id"]
        # unique_together = ("recipe", "ingredient")
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_ingredient_item"
            )
        ]

    def __str__(self):
        return self.ingredient.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite_recipe"
            )
        ]

    def __str__(self):
        return "Пользователь {} добавил {} в избранное.".format(
            self.user.username, self.recipe.name
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Объект списка покупок"
        verbose_name_plural = "Объекты списка покупок"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="Unique ShoppingCart for user and recipe",
            )
        ]

    def __str__(self):
        return (
            f"Рецепт {self.recipe.name} из корзины покупок "
            f"пользователя {self.user.username}."
        )
