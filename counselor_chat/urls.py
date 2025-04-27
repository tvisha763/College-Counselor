from django.urls import path
from . import views
app_name = "counselor_chat"
urlpatterns = [
    path('api/chat/', views.chat_view, name='chat'),
]
