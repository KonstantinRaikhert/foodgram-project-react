from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import RecipeFilter
from recipes.models import FavoriteRecipe, Ingredient, Recipe, Tag
from recipes.serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipePostSerializer,
    RecipeSerializer,
    TagSerializer,
)
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by("-id")
        is_favorited = self.request.query_params.get("is_favorited")
        favorite = FavoriteRecipe.objects.filter(user=self.request.user.id)

        if is_favorited == "true":
            queryset = queryset.filter(favoriterecipe__in=favorite)
        elif is_favorited == "false":
            queryset = queryset.exclude(favoriterecipe__in=favorite)
        return queryset.all().order_by("-id")

    def get_serializer_class(self):
        if self.action != "list" and self.action != "retrieve":
            return RecipePostSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["GET", "DELETE"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        serializer = FavoriteRecipeSerializer(
            data={"recipe": pk, "user": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "GET":
            serializer.save()
            return Response(
                {"status": "Рецепт добавлен в избранное"},
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            recipe = self.get_object()
            number_deleted_objects, _ = FavoriteRecipe.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()

            if number_deleted_objects == 0:
                raise serializers.ValidationError(
                    {"message": "Вы еще не добавили этот рецепт в избранное."}
                )
            return Response(
                {"status": "Рецепт удалён из избранного"},
                status=status.HTTP_204_NO_CONTENT,
            )

    # @action(
    #     detail=True,
    #     methods=["GET", "DELETE"],
    #     url_path="favorite",
    #     url_name="favorite",
    #     permission_classes=[permissions.IsAuthenticated],
    # )
