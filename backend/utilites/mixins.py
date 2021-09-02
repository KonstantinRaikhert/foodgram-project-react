from django.contrib import admin
from django.utils.html import format_html


class AdminColor:

    """
    Mixin makes colored circles from the colors used in the object
    Add this field in admin class
        list_display = ("colored_circle",)
    """

    @admin.display(
        description="Цвет",
    )
    def colored_circle(self, obj):
        return format_html(
            "<span style='"
            "height: 25px;"
            "width: 25px;"
            "border: 1px solid grey;"
            "border-radius: 50%;"
            "display: inline-block;"
            "background-color: {};'>"
            "</span>",
            obj.color,
        )
