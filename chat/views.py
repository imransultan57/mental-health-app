from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegisterForm
from .models import ChatMessage
import openai
from openai import OpenAI
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.http import JsonResponse
from openai import OpenAI, RateLimitError
from django.conf import settings
from django.http import JsonResponse
from django.conf import settings
from groq import Groq
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from textblob import TextBlob



def home(request):
    return render(request, "chat/home.html")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chat")
    else:
        form = RegisterForm()
    return render(request, "chat/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("chat")
    else:
        form = AuthenticationForm()
    return render(request, "chat/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")



# Simple supportive responses
SUPPORTIVE_RESPONSES = {
    "positive": [
        "That’s great to hear! Keep it up 🌟",
        "I’m glad you’re feeling good today 💚",
        "That’s wonderful! Stay motivated 🙌"
    ],
    "neutral": [
        "I hear you. Sometimes it helps to take a deep breath 🌿",
        "I’m here to listen, no matter what 🤝",
        "Thanks for sharing. You’re not alone 💜"
    ],
    "negative": [
        "I’m sorry you feel this way 💔 Remember, it’s okay to have bad days.",
        "You are not alone. Things will get better, one step at a time 🌈",
        "That sounds tough 😞. Please know I’m here to listen and support you."
    ]
}

@login_required
def chat_view(request):
    chats = ChatMessage.objects.all().order_by("-timestamp")[:50]  # latest 50 messages

    if request.method == "POST":
        user_msg = request.POST.get("query")
        if user_msg.strip():
            # Save user message
            ChatMessage.objects.create(user=request.user, message=user_msg)

            # Sentiment Analysis
            blob = TextBlob(user_msg)
            polarity = blob.sentiment.polarity

            if polarity > 0.2:
                response = SUPPORTIVE_RESPONSES["positive"][0]
            elif polarity < -0.2:
                response = SUPPORTIVE_RESPONSES["negative"][0]
            else:
                response = SUPPORTIVE_RESPONSES["neutral"][0]

            # Save bot response (Jarvis)
            ChatMessage.objects.create(
                user=request.user,  # you can also create a separate bot user
                message=f"Jarvis: {response}"
            )

        return redirect("chat")  # reload page

    return render(request, "chat/chat.html", {"chats": chats})








client = Groq(api_key=settings.GROQ_API_KEY)

@login_required
def chat_api(request):
    query = request.GET.get("query", "")
    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # or "mixtral-8x7b-32768"
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": query},
        ],
    )

    answer = response.choices[0].message.content

    # save to DB
   # Save user message
    ChatMessage.objects.create(user=request.user, message=f"You: {query}")
    # Save AI response
    ChatMessage.objects.create(user=request.user, message=f"Jarvis: {answer}")

    return JsonResponse({"response": answer})
