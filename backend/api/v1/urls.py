from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


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
]
