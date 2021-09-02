from django.db import models
from django.utils.translation import gettext_lazy
from management.utils import slugify


class Tag(models.Model):
    class Color(models.TextChoices):
        ORANGE = "#E26C2D", gettext_lazy("Оранжевый")
        GREEN = "#49B64E", gettext_lazy("Зелёный")
        PURPLE = "#8775D2", gettext_lazy("Фиолетовый")

    name = models.CharField(max_length=50, unique=True)
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
