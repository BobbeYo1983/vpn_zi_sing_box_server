from rest_framework.viewsets import ModelViewSet
from .models import VpnUser
from .serializers import VpnUserSerializer
from .singbox import write_config, reload_singbox

class VpnUserViewSet(ModelViewSet):
    queryset = VpnUser.objects.all()
    serializer_class = VpnUserSerializer

    def perform_create(self, serializer):
        serializer.save()
        write_config()
        reload_singbox()

    def perform_update(self, serializer):
        serializer.save()
        write_config()
        reload_singbox()

    def perform_destroy(self, instance):
        instance.delete()
        write_config()
        reload_singbox()
