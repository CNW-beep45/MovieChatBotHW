from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q  # Added this import
from .models import Show, ChatMessage
from .utils import ChatBotNLP
import json

chatbot = ChatBotNLP()

def index(request):
    return render(request, 'chatbot/index.html')

@csrf_exempt
def chat_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        # Save user message
        ChatMessage.objects.create(message=user_message, is_bot=False)

        # Process message with NLP
        genres = chatbot.extract_genres(user_message)
        shows = Show.objects.all()

        # Filter by genres if found
        if genres:
            genre_filter = Q()
            for genre in genres:
                genre_filter |= Q(genre__icontains=genre)
            shows = shows.filter(genre_filter)

        # Sort by rating and get top results
        shows = shows.order_by('-rating')[:3]

        # Generate response
        response = chatbot.generate_response(user_message, shows)

        # Save bot message
        ChatMessage.objects.create(message=response['message'], is_bot=True)

        return JsonResponse({
            'message': response['message'],
            'recommendations': [
                {
                    'title': show.title,
                    'genre': show.genre,
                    'rating': show.rating,
                    'description': show.description
                } for show in shows
            ] if response['requires_recommendation'] else []
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)