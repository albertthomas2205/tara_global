from django.urls import re_path
from .consumers import RobotConsumer

websocket_urlpatterns = [
    re_path(r'^ws/robots/(?P<robo_id>[^/]+)/$', RobotConsumer.as_asgi()),
]
