from rest_framework.viewsets import ModelViewSet
from .models import VpnUser
from .serializers import VpnUserSerializer
from .singbox import write_config
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class VpnUserViewSet(ModelViewSet):
    queryset = VpnUser.objects.all()
    serializer_class = VpnUserSerializer
    permission_classes = [AllowAny] 
    authentication_classes = []  # временно отключаем

    # приватный метод для повторяющихся действий
    def _after_change(self):
        write_config()

    def create(self, request, *args, **kwargs):
        tg_id = request.data.get("tg_id")
        tg_username = request.data.get("tg_username")

        logger.info(
            "Запрос на создание VPN пользователя",
            extra={
                "tg_id": tg_id,
                "tg_username": tg_username,
            },
        )

        # Проверяем существование пользователя
        if VpnUser.objects.filter(tg_id=tg_id).exists():
            logger.warning(
                "Попытка создать уже существующего VPN пользователя",
                extra={
                    "tg_id": tg_id,
                    "tg_username": tg_username,
                },
            )
            return Response(
                {"detail": "Пользователь уже существует"},
                status=status.HTTP_409_CONFLICT,
            )

        # Создаём пользователя
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.info(
            "VPN пользователь успешно создан",
            extra={
                "vpn_user_id": user.id,
                "tg_id": user.tg_id,
                "tg_username": tg_username,
            },
        )

        # Побочные действия
        self._after_change()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
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
        Удаляет всех пользователей из БД и пересоздаёт конфиг.
        """
        count, _ = VpnUser.objects.all().delete()
        self._after_change()
        return Response(
            {"detail": f"Deleted {count} users"},
            status=status.HTTP_200_OK
        )
