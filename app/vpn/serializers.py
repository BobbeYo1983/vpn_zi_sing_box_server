from rest_framework import serializers
from .models import SingBoxUser
from .singbox import build_vless_uri
from rest_framework.validators import UniqueValidator

class SingBoxUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.CharField(
        max_length=64,
        validators=[UniqueValidator(queryset=SingBoxUser.objects.all())]
    )
    vless_uri = serializers.SerializerMethodField()

    class Meta:
        model = SingBoxUser
        fields = "__all__"

    def get_vless_uri(self, obj):
        return build_vless_uri(obj)
