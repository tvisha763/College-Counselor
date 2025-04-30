from django.urls import path
from . import views

app_name = 'counselor_chat'
urlpatterns = [
    path('api/chat/', views.chat_view, name='chat'),
    path('get_chat_history/', views.get_chat_history, name='get_chat_history'),
    path('save_chat_message/', views.save_chat_message, name='save_chat_message'),
]
