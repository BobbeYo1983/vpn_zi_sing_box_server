from rest_framework import serializers
from .models import VpnUser
from .singbox import build_vless_uri
from rest_framework.validators import UniqueValidator

class VpnUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=50,
        validators=[UniqueValidator(queryset=VpnUser.objects.all())]
    )
    vless_uri = serializers.SerializerMethodField()

    class Meta:
        model = VpnUser
        fields = ['id', 'name', 'uuid', 'enabled', 'vless_uri']

    def get_vless_uri(self, obj):
        return build_vless_uri(obj)
