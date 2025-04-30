import sys
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings

from counselor_chat.models import SystemPrompt


@receiver(post_migrate)
def load_system_prompts(sender, **kwargs):
    # Optional: only run this during `runserver` or specific commands
    if 'runserver' not in sys.argv and 'migrate' not in sys.argv:
        return

    prompts = settings.SYSTEM_PROMPTS

    for page, prompt in prompts.items():
        obj, created = SystemPrompt.objects.update_or_create(
            page_identifier=page,
            defaults={"prompt_text": prompt},
        )
        action = "Created" if created else "Updated"
        print(f"[{action}] prompt for page: {page}")
