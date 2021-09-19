from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import RecipeFilter
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientItem,
    Recipe,
    ShoppingCart,
    Tag,
)
from recipes.serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipePostSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xhtml2pdf import pisa

FAVORITE_RECIPE_ERROR = serializers.ValidationError(
    {"message": "Вы еще не добавили этот рецепт в избранное."}
)
SHOPPINGCART_RECIPE_ERROR = serializers.ValidationError(
    {"message": "Вы еще не добавили этот рецепт в корзину покупок."}
)
SHOPPINGCART_EMPTY_ERROR = serializers.ValidationError(
    {"message": "Список покупок пуст..."}
)
CREATE_PDF_ERROR = serializers.ValidationError(
    {"message": "Не удалось подготовить PDF файл."}
)
METHOD_GET = "GET"
METHOD_DELETE = "DELETE"


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
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

    # @action(
    #     detail=False,
    #     methods=[
    #         "get",
    #     ],
    #     url_path="<pk>/favorite",
    #     url_name="get-favorite",
    #     permission_classes=[permissions.IsAuthenticated],
    # )
    # def get_favorite(self, request, pk):
    #     serializer = FavoriteRecipeSerializer(
    #         data={"recipe": pk, "user": request.user.id}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     # if request.method == METHOD_GET:
    #     serializer.save()
    #     return Response(
    #         {"status": "Рецепт добавлен в избранное"},
    #         status=status.HTTP_201_CREATED,
    #     )

    # @action(
    #     detail=True,
    #     methods=METHOD_DELETE,
    #     url_path="favorite",
    #     # url_name="favorite",
    #     permission_classes=[permissions.IsAuthenticated],
    # )
    # def delete_favorite(self, request, pk):
    #     recipe = self.get_object()
    #     number_deleted_objects, _ = FavoriteRecipe.objects.filter(
    #         user=request.user,
    #         recipe=recipe,
    #     ).delete()
    #     if number_deleted_objects == 0:
    #         raise FAVORITE_RECIPE_ERROR
    #     return Response(
    #         {"status": "Рецепт удалён из избранного"},
    #         status=status.HTTP_204_NO_CONTENT,
    #     )

    @action(
        detail=True,
        methods=(METHOD_GET, METHOD_DELETE),
        url_path="favorite",
        url_name="favorite",
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        serializer = FavoriteRecipeSerializer(
            data={"recipe": pk, "user": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == METHOD_GET:
            serializer.save()
            return Response(
                {"status": "Рецепт добавлен в избранное"},
                status=status.HTTP_201_CREATED,
            )
        if request.method == METHOD_DELETE:
            recipe = self.get_object()
            number_deleted_objects, _ = FavoriteRecipe.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            if number_deleted_objects == 0:
                raise FAVORITE_RECIPE_ERROR
            return Response(
                {"status": "Рецепт удалён из избранного"},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=True,
        methods=("GET", "DELETE"),
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        serializer = ShoppingCartSerializer(
            data={"recipe": pk, "user": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "GET":
            serializer.save()
            return Response(
                {"status": "Рецепт добавлен в корзину покупок"},
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            recipe = self.get_object()
            number_deleted_objects, _ = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()

            if number_deleted_objects == 0:
                raise SHOPPINGCART_RECIPE_ERROR
            return Response(
                {"status": "Рецепт удалён из корзины покупок"},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        queryset = IngredientItem.objects.filter(
            recipe__shoppingcart__user=user
        )
        if not queryset.exists():
            raise SHOPPINGCART_EMPTY_ERROR
        context = {"ingredient_list": queryset}
        context["STATIC_ROOT"] = settings.STATIC_ROOT

        template_path = "cart_list_pdf.html"
        template = get_template(template_path)
        html = template.render(context)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="cart.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            raise CREATE_PDF_ERROR
        return response
