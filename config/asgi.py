"""
ASGI config for django_socketio project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from socket_io.views import app as socket_app
from channels.routing import ProtocolTypeRouter


django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": socket_app,
    }
)
app = application
