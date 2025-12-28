from rest_framework import serializers
from .models import VpnUser
from .singbox import build_vless_uri
from rest_framework.validators import UniqueValidator

class VpnUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.CharField(
        max_length=64,
        validators=[UniqueValidator(queryset=VpnUser.objects.all())]
    )
    vless_uri = serializers.SerializerMethodField()

    class Meta:
        model = VpnUser
        fields = "__all__"
        read_only_fields = ("enabled",)

    def get_vless_uri(self, obj):
        return build_vless_uri(obj)
