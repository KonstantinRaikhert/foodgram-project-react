from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import CustomUser, Subscribe
from users.serializers import (
    AuthorSerializer,
    SubscribeSerializer,
    UserChangePasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
)

UNSUBSCRIBE_ERROR = serializers.ValidationError(
    {"message": "Нельзя отписаться, Вы ещё не подписаны!"}
)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action != "list" and self.action != "retrieve":
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=("GET", "PATCH", "PUT"),
        url_path="me",
        url_name="me",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def view_me(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid() and request.method in ("PATCH",):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=("GET", "DELETE"),
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        serializer = SubscribeSerializer(
            data={
                "author": pk,
                "subscriber": request.user.id,
            }
        )
        if request.method in ("GET",):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"status": "Подписка осуществлена"},
                status=status.HTTP_201_CREATED,
            )
        serializer.is_valid(raise_exception=True)
        if not Subscribe.objects.filter(**serializer.validated_data):
            raise UNSUBSCRIBE_ERROR

        unsubscribe = get_object_or_404(Subscribe, **serializer.validated_data)
        unsubscribe.delete()
        return Response(
            {"status": "Отписка осуществлена"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriber = CustomUser.objects.filter(
            author__in=request.user.subscriber.all()
        ).order_by("id")
        page = self.paginate_queryset(subscriber)
        if page is not None:
            serializer = AuthorSerializer(
                subscriber, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = AuthorSerializer(
            subscriber, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=("POST",),
        url_path="set_password",
        url_name="set_password",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"status": "Пароль изменен"}, status=status.HTTP_201_CREATED
        )
