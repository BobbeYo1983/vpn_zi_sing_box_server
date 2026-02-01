from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import SingBoxUser
from .serializers import SingBoxUserSerializer
from .singbox import write_config
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class SingBoxUserViewSet(ModelViewSet):
    queryset = SingBoxUser.objects.all()
    serializer_class = SingBoxUserSerializer
    permission_classes = [AllowAny] 
    authentication_classes = []

    # приватный метод для повторяющихся действий
    def _after_change(self):
        write_config()

    def create(self, request, *args, **kwargs):
        """Создаёт или активирует sing-box-пользователя"""

        tg_id = request.data.get("tg_id")
        tg_username = request.data.get("tg_username")

        extra_info_user={"tg_id": tg_id, "tg_username": tg_username}

        logger.info("Создание/активация sing-box-пользователя", extra=extra_info_user)

        # Пытаемся найти существующего пользователя
        user = SingBoxUser.objects.filter(tg_id=tg_id).first()

        if user:
            # Если есть — просто активируем
            if not user.active:
                user.active = True
                user.save(update_fields=["active"])
                self._after_change()
                logger.debug("Существующий sing-box-пользователь активирован", extra={"id": user.id, **extra_info_user})
            else:
                logger.warning("Существующий sing-box-пользователь уже активирован", extra={"id": user.id, **extra_info_user})

            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Если нет — создаём нового
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self._after_change()
        logger.debug("Sing-box-пользователь успешно создан", extra={"id": user.id, **extra_info_user})

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(self, serializer):
        serializer.save()
        self._after_change()

    def perform_destroy(self, instance):
        instance.delete()
        self._after_change()

    @action(detail=False, methods=["delete"], url_path="delete_all")
    def delete_all_users(self, request):
        """
        Удаляет всех sing-box-пользователей из БД и пересоздаёт конфиг.
        """
        count, _ = SingBoxUser.objects.all().delete()
        self._after_change()
        return Response(
            {"detail": f"Deleted {count} users"},
            status=status.HTTP_200_OK
        )

    @action(methods=["post"], detail=False, url_path="deactivate")
    def deactivate(self, request):
        """Деактивирует sing-box-пользователя, но оставляет в БД."""

        tg_id = request.data.get("tg_id")
        tg_username = request.data.get("tg_username")
        extra_info_user={"tg_id": tg_id, "tg_username": tg_username}

        logger.info("Деактивация sing-box-пользователя", extra=extra_info_user)

        if not tg_id or not tg_username:
            msg = "Sing-box пользователь не деактивирован по запросу, так как поля tg_id и tg_username обязательны"
            logger.error(msg)
            return Response(
                {"detail": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(SingBoxUser, tg_id=tg_id)
        user.active = False
        user.save(update_fields=["active"])

        self._after_change()

        return Response(status=status.HTTP_204_NO_CONTENT)
