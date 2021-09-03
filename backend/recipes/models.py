from django.db import models
from django.utils.translation import gettext_lazy
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
        verbose_name="Название", max_length=200, unique=True, blank=False
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=10,
        unique=True,
        blank=False,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["id"]

    def __str__(self):
        return self.name
