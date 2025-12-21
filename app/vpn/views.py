from rest_framework.viewsets import ModelViewSet
from .models import VpnUser
from .serializers import VpnUserSerializer
from .singbox import write_config, check_config, reload_singbox

class VpnUserViewSet(ModelViewSet):
    queryset = VpnUser.objects.all()
    serializer_class = VpnUserSerializer

    # приватный метод для повторяющихся действий
    def _after_change(self):
        write_config()
        check_config()
        # reload_singbox()  # включить на проде

    def perform_create(self, serializer):
        serializer.save()
        self._after_change()

    def perform_update(self, serializer):
        serializer.save()
        self._after_change()

    def perform_destroy(self, instance):
        instance.delete()
        self._after_change()
