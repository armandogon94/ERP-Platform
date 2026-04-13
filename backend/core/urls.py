from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import ModuleViewSet, ViewDefinitionViewSet

router = DefaultRouter()
router.register("modules", ModuleViewSet, basename="module")
router.register("views", ViewDefinitionViewSet, basename="viewdefinition")

urlpatterns = [
    path("", include(router.urls)),
]
