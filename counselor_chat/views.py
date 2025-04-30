from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import json

from .services import ChatService
from .models import ChatHistory
from .utils import store_in_session, get_session_history
from .system_prompts import generate_system_prompt
from counselor.models import User

@login_required(login_url='counselor:login')
def chat_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=400)

    user_input = request.POST.get("message")
    page_identifier = request.POST.get("page_identifier")
    subject = request.POST.get("subject", "").strip()
    system_prompt = generate_system_prompt(page_identifier, subject)
    user_instance = request.user

    past_messages = ChatHistory.objects.filter(
        user=user_instance,
        page_identifier=page_identifier
    ).order_by('timestamp')
    history = [{"role": h.role, "content": h.message} for h in past_messages]

    chat_service = ChatService(system_prompt, history)
    ai_reply = chat_service.chat(user_input, user=user_instance)

    ChatHistory.objects.create(
        user=user_instance,
        page_identifier=page_identifier,
        role='user',
        message=user_input,
        timestamp=now()
    )
    ChatHistory.objects.create(
        user=user_instance,
        page_identifier=page_identifier,
        role='assistant',
        message=ai_reply,
        timestamp=now()
    )

    store_in_session(request, page_identifier, 'user', user_input)
    store_in_session(request, page_identifier, 'assistant', ai_reply)

    return JsonResponse({"reply": ai_reply})


@login_required(login_url='counselor:login')
def get_chat_history(request):
    page_id = request.GET.get("page_identifier")
    if not page_id:
        return JsonResponse({"error": "Missing page_identifier"}, status=400)

    chat_entries = ChatHistory.objects.filter(
        user=request.user,
        page_identifier=page_id
    ).order_by("timestamp")

    messages = [
        {
            "role": entry.role,
            "message": entry.message,
            "timestamp": entry.timestamp.strftime("%Y-%m-%d at %H:%M:%S")
        }
        for entry in chat_entries
    ]

    return JsonResponse({"messages": messages})


@require_POST
@login_required(login_url='counselor:login')
def save_chat_message(request):
    try:
        data = json.loads(request.body)
        page_id = data.get("page_identifier")
        role = data.get("role")
        message = data.get("message")

        if not all([page_id, role, message]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        ChatHistory.objects.create(
            user=request.user,
            page_identifier=page_id,
            role=role,
            message=message,
            timestamp=now()
        )

        return JsonResponse({"status": "success"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
