from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
from .models import Show, ChatMessage
from .utils import EnhancedChatBotNLP
import json
import os

# Import the TMDB client
from .tmdb_client import TMDBClient

# Initialize the enhanced NLP chatbot and TMDB client
chatbot = EnhancedChatBotNLP()
tmdb_client = TMDBClient()


def index(request):
    """Render the main chat interface"""
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
        intents = chatbot.extract_intent(user_message)

        print(f"User message: {user_message}")
        print(f"Detected genres: {genres}")
        print(f"Detected intents: {intents}")

        # Get shows based on detected genres
        shows = []
        if genres:
            genre_filter = Q()
            for genre in genres:
                genre_filter |= Q(genre__icontains=genre)
            shows = Show.objects.filter(genre_filter).order_by('-rating')[:3]

        # If no shows found or no genres detected, get some default shows
        if not shows:
            shows = Show.objects.all().order_by('-rating')[:3]

        # Generate response
        response = chatbot.generate_response(user_message, shows)

        # Debug
        print(f"Response: {response}")
        print(f"Shows found: {[show.title for show in shows]}")

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


def populate_database(request):
    """Admin function to populate the database with initial movie data"""
    if request.user.is_staff:  # Only staff/admin can access this
        try:
            # Get popular movies from TMDB
            popular_movies = tmdb_client.get_popular_movies(page=1)
            count = 0

            if popular_movies and 'results' in popular_movies:
                for movie in popular_movies['results']:
                    # Get more details about the movie
                    details = tmdb_client.get_movie_details(movie['id'])

                    if details:
                        # Extract genres
                        genres = ', '.join([genre['name'] for genre in details.get('genres', [])])

                        # Create new show if it doesn't exist
                        if not Show.objects.filter(title=details['title']).exists():
                            Show.objects.create(
                                title=details['title'],
                                genre=genres,
                                rating=details['vote_average'],
                                description=details['overview']
                            )
                            count += 1

            return JsonResponse({'success': True, 'message': f'Added {count} movies to database'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)


def chat_history(request):
    """View to display the chat history"""
    messages = ChatMessage.objects.all().order_by('timestamp')
    return render(request, 'chatbot/history.html', {'messages': messages})