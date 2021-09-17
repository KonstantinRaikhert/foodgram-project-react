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

    name = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        verbose_name="Название тега",
        help_text="Введите название тега",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Уникальная строка идентификатор",
        help_text="Можно указать кириллицей (автоматическая транслитерация)",
    )
    color = models.CharField(
        verbose_name="Цвет тега",
        max_length=8,
        choices=Color.choices,
        help_text="Выберите цвет из списка",
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
        verbose_name="Название",
        max_length=200,
        blank=False,
        help_text="Укажите название ингредиента",
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=10,
        blank=False,
        help_text="Укажите единицы измерения ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Выберите автора из списка",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientItem",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
        help_text="Выберите ингредиенты из списка",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        help_text="Выберите теги из списка",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Введите название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Изображение",
        help_text="Загрузите фотографию",
    )
    text = models.TextField(
        verbose_name="Описание",
        help_text="Опишите весь рецепт",
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(1),),
        verbose_name="Время приготовления",
        help_text="Укажите время приготовления в минутах",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
        help_text="Выберите рецепт из списка",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
        help_text="Выберите ингредиент из списка",
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(1),),
        verbose_name="Количество",
        help_text="Укажите количество ингредиента в рецепте",
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_ingredient_item"
            ),
        )

    def __str__(self):
        return self.ingredient.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт для добавления в избранное",
    )

    class Meta:
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe"
            ),
        )

    def __str__(self):
        return (
            f"Пользователь {self.user.username} добавил "
            f"{self.recipe.name} в избранное."
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт для добавления в корзину покупок",
    )

    class Meta:
        verbose_name = "Объект списка покупок"
        verbose_name_plural = "Объекты списка покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="Unique ShoppingCart for user and recipe",
            ),
        )

    def __str__(self):
        return (
            f"Рецепт {self.recipe.name} из корзины покупок "
            f"пользователя {self.user.username}."
        )
