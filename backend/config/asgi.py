import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # WebSocket routing will be added in Slice 19
        # "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
