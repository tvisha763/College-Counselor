from counselor_chat.models import SystemPrompt

def generate_system_prompt(page_identifier: str, subject=None) -> str:
    try:
        system_prompt = SystemPrompt.objects.get(page_identifier=page_identifier)
        if page_identifier == "_tutoring" and subject:
            return f"{system_prompt.prompt_text} The student needs help with {subject}."
        return system_prompt.prompt_text
    except SystemPrompt.DoesNotExist:
        return (
            "You are a college application tracking assistant. On this page, users are monitoring the progress of their applications. Help the user stay organized by summarizing what steps are complete, what is pending, and suggesting next actions. Encourage timely follow-ups and offer reminders about common missing items (like transcripts or recommendation letters)."
        )
