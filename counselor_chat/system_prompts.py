from counselor_chat.models import SystemPrompt


def generate_system_prompt(page_identifier: str, subject=None) -> str:
    try:
        system_prompt = SystemPrompt.objects.get(
            page_identifier=page_identifier
        )
        if page_identifier == "_tutoring" and subject:
            return f"{system_prompt.prompt_text} The student needs help with {subject}."
        return system_prompt.prompt_text
    except SystemPrompt.DoesNotExist:
        return "You are a college application tracking assistant helping students stay organized and on track. On this page, users are reviewing the status of their applications. Clearly summarize completed tasks, outstanding items, and urgent next steps. Provide helpful reminders about common application components such as essays, transcripts, test scores, and recommendation letters. Encourage follow-through to meet all deadlines."
