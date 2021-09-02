from django.urls import path
from django.urls.conf import include
from recipes.views import TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
]
