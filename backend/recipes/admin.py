from django.contrib import admin
from recipes.models import Tag
from utilites.mixins import AdminColor


class TagAdmin(AdminColor, admin.ModelAdmin):
    list_display = ("name", "slug", "colored_circle")
    prepopulated_fields = {
        "slug": ["name"],
    }
    ordering = ("id",)


admin.site.register(Tag, TagAdmin)
