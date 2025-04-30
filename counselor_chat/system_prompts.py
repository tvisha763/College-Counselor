from counselor_chat.models import SystemPrompt

def generate_system_prompt(page_identifier: str, subject=None) -> str:
    try:
        system_prompt = SystemPrompt.objects.get(page_identifier=page_identifier)
        if page_identifier == "_tutoring" and subject:
            return f"{system_prompt.prompt_text} The student needs help with {subject}."
        return system_prompt.prompt_text
    except SystemPrompt.DoesNotExist:
        return (
            "You are a helpful assistant for the college counselor platform. "
            "Answer student questions clearly and positively."
        )
