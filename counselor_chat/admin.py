from django.contrib import admin
from .models import ChatHistory, SystemPrompt

admin.site.register(ChatHistory)
admin.site.register(SystemPrompt)
