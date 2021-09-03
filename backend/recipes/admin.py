from django.contrib import admin
from recipes.models import Ingredient, Tag
from utilites.mixins import AdminColor


class TagAdmin(AdminColor, admin.ModelAdmin):
    list_display = ("name", "slug", "colored_circle")
    prepopulated_fields = {
        "slug": ["name"],
    }
    ordering = ("id",)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
    ordering = ("name",)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
