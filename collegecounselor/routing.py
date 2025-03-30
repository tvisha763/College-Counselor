from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # For one-to-one chats using user IDs
    re_path(r'ws/chat/(?P<receiver_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Optional: Add these if you need group/room functionality later
    # re_path(r'ws/group/(?P<group_id>\d+)/$', consumers.GroupChatConsumer.as_asgi()),
    # re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
