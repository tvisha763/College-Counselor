from django.db import models

from counselor.models import User


class ChatHistory(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_identifier = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_vectordb_text(self):
        return f"{self.user.email} -- {self.role} -- {self.page_identifier} -- {self.message}"

    def get_vectordb_metadata(self):
        return {
            "user_id": self.user.id,
            "role": self.role,
            "page_identifier": self.page_identifier,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self):
        return f"{self.user.email} ({self.role}) @ {self.page_identifier}"


class SystemPrompt(models.Model):
    page_identifier = models.CharField(max_length=100, unique=True)
    prompt_text = models.TextField()

    def __str__(self):
        return f"Prompt for {self.page_identifier}"

    def get_vectordb_text(self):
        return f"{self.page_identifier} -- {self.prompt_text}"

    def get_vectordb_metadata(self):
        return {
            "page_identifier": self.page_identifier,
            "description": self.prompt_text,
        }

    class Meta:
        verbose_name = "System Prompt"
        verbose_name_plural = "System Prompts"
