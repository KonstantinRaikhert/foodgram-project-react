from recipes.models import Tag
from recipes.serializers import TagSerializer
from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("id")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
