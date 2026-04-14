from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.auth import LoginView, LogoutView, MeView, RefreshView


class APIRootView(APIView):
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "name": "ERP Platform API",
                "version": "1.0.0",
                "status": "ok",
            }
        )


urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    # Auth
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    # Core
    path("core/", include("core.urls")),
    # ERP modules
    path("hr/", include("modules.hr.urls")),
    path("calendar/", include("modules.calendar.urls")),
    path("inventory/", include("modules.inventory.urls")),
    path("purchasing/", include("modules.purchasing.urls")),
    path("sales/", include("modules.sales.urls")),
]
