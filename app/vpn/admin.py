from django.contrib import admin
from .models import SingBoxUser

@admin.register(SingBoxUser)
class SingBoxUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SingBoxUser._meta.fields]