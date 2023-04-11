from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/regenerate/", consumers.RegenerateConsumer.as_asgi()),
]

