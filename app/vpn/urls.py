from rest_framework.routers import DefaultRouter
from .views import SingBoxUserViewSet

router = DefaultRouter()
router.register("users", SingBoxUserViewSet)

urlpatterns = router.urls