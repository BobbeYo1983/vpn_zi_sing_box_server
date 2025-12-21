from rest_framework import serializers
from .models import VpnUser
from .singbox import build_vless_uri

class VpnUserSerializer(serializers.ModelSerializer):
    vless_uri = serializers.SerializerMethodField()

    class Meta:
        model = VpnUser
        fields = ["id", "name", "uuid", "enabled", "vless_uri"]

    def get_vless_uri(self, obj):
        return build_vless_uri(obj)
