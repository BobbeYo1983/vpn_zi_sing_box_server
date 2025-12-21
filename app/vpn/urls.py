from rest_framework.routers import DefaultRouter
from .views import VpnUserViewSet

router = DefaultRouter()
router.register("users", VpnUserViewSet)

urlpatterns = router.urls