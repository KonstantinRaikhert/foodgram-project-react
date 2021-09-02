from recipes.models import Tag
from recipes.serializers import TagSerializer
from rest_framework import generics


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all().order_by("id")
    serializer_class = TagSerializer
