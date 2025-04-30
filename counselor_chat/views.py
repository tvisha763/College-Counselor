<<<<<<< HEAD
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import ChatService
from .models import ChatHistory
from .utils import store_in_session, get_session_history
from .system_prompts import generate_system_prompt

from counselor.models import User

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        user_input = request.POST.get("message")
        page_identifier = request.POST.get("page_identifier")
        system_prompt = generate_system_prompt(page_identifier)

        # # TESTING
        # return JsonResponse({"reply": "pong\n" + user_input + "\n" + system_prompt})

        user_instance =  user = User.objects.get(email=request.session["email"])

        past_messages = ChatHistory.objects.filter(
            user=user_instance,
            page_identifier=page_identifier
        ).order_by('timestamp')

        history = [{"role": h.role, "content": h.message} for h in past_messages]

        chat_service = ChatService(system_prompt, history)
        ai_reply = chat_service.chat(user_input)

        ChatHistory.objects.create(
            user=user_instance,
            page_identifier=page_identifier,
            role='user',
            message=user_input
        )
        ChatHistory.objects.create(
            user=user_instance,
            page_identifier=page_identifier,
            role='assistant',
            message=ai_reply
        )

        store_in_session(request, page_identifier, 'user', user_input)
        store_in_session(request, page_identifier, 'assistant', ai_reply)

        return JsonResponse({"reply": ai_reply})

    return JsonResponse({"error": "Invalid method"}, status=400)


=======
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import ChatService
from .models import ChatHistory
from .utils import store_in_session, get_session_history
from .system_prompts import generate_system_prompt

from counselor.models import User

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        user_input = request.POST.get("message")
        page_identifier = request.POST.get("page_identifier")
        system_prompt = generate_system_prompt(page_identifier)

        # # TESTING
        # return JsonResponse({"reply": "pong\n" + user_input + "\n" + system_prompt})

        user_instance =  user = User.objects.get(email=request.session["email"])

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
            message=user_input
        )
        ChatHistory.objects.create(
            user=user_instance,
            page_identifier=page_identifier,
            role='assistant',
            message=ai_reply
        )

        store_in_session(request, page_identifier, 'user', user_input)
        store_in_session(request, page_identifier, 'assistant', ai_reply)

        return JsonResponse({"reply": ai_reply})

    return JsonResponse({"error": "Invalid method"}, status=400)
>>>>>>> main
