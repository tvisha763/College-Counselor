from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ChatService:
    def __init__(self, system_prompt, history):
        self.system_prompt = system_prompt
        self.history = history or []

    def chat(self, user_input):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.history
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(model="gpt-4",
        messages=messages,
        )

        reply = response.choices[0].message.content
        return reply
