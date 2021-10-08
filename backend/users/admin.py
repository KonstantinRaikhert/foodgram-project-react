from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from users.models import CustomUser, Subscribe


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "last_login",
        "count",
    )
    exclude = ("groups", "user_permissions")
    readonly_fields = ("is_superuser",)
    list_display_links = ("first_name", "last_name", "email")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("date_joined",)

    def count(self, obj):
        count = obj.author.count()
        return format_html("<a>{}</a>", count)

    count.short_description = "Подписчиков"


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("author", "subscriber")
    search_fields = ("author__username",)
    ordering = ("id",)


admin.site.unregister(Group)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
