from django.urls import path
from recipes.views import TagList

# from django.urls.conf import include


urlpatterns = [
    path("tags/", TagList.as_view(), name="tags"),
]
