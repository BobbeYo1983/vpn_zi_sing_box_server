from rest_framework.viewsets import ModelViewSet
from .models import VpnUser
from .serializers import VpnUserSerializer
from .singbox import write_config#, check_config, reload_singbox
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class VpnUserViewSet(ModelViewSet):
    queryset = VpnUser.objects.all()
    serializer_class = VpnUserSerializer
    permission_classes = [AllowAny] 
    authentication_classes = []  # временно отключаем

    # приватный метод для повторяющихся действий
    def _after_change(self):
        write_config()
        #check_config()
        #reload_singbox()

    def perform_create(self, serializer):
        serializer.save()
        self._after_change()

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
