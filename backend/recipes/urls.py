from django.urls import path
from django.urls.conf import include
from recipes.views import IngredientViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
]
