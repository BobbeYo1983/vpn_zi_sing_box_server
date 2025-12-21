import uuid
from django.db import models

class VpnUser(models.Model):
    name = models.CharField(max_length=64)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
