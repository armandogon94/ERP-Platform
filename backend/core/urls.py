from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import ModuleViewSet

router = DefaultRouter()
router.register("modules", ModuleViewSet, basename="module")

urlpatterns = [
    path("", include(router.urls)),
]
