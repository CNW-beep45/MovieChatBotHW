from django.shortcuts import render
from django.http import JsonResponse
from django.template.backends import django
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
from .models import Show, ChatMessage
from .utils import EnhancedChatBotNLP
from django.utils import timezone
import json
import os
import logging
import traceback

import random

from .tmdb_client import TMDBClient

chatbot = EnhancedChatBotNLP()
tmdb_client = TMDBClient()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('chatbot')

def index(request):
    """Render the main chat interface"""
    return render(request, 'chatbot/index.html')


@csrf_exempt
def chat_message(request):
    """Handle chat messages with detailed error tracking"""
    # Create a log file in the project root for debugging
    import logging
    logging.basicConfig(
        filename='chatbot_error.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('chatbot_debug')

    if request.method == 'POST':
        try:
            logger.debug("Received POST request to chat_message")

            # Attempt to parse the JSON data
            try:
                data = json.loads(request.body)
                logger.debug(f"Successfully parsed JSON data: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}")
                logger.debug(f"Request body: {request.body}")
                return JsonResponse({
                    'message': 'Sorry, there was an error processing your request. Invalid JSON data.',
                    'error': str(e)
                }, status=400)

            # Get the message from the data
            user_message = data.get('message', '')
            if not user_message:
                logger.warning("No message found in request data")
                return JsonResponse({
                    'message': 'Sorry, I didn\'t receive any message to process.',
                }, status=400)

            logger.debug(f"Processing user message: '{user_message}'")

            # Save user message
            try:
                ChatMessage.objects.create(message=user_message, is_bot=False)
                logger.debug("Saved user message to database")
            except Exception as e:
                logger.error(f"Error saving user message: {str(e)}")
                # Continue processing even if saving fails

            # Process message with NLP
            try:
                genres = chatbot.extract_genres(user_message)
                intents = chatbot.extract_intent(user_message)
                logger.debug(f"Extracted genres: {genres}")
                logger.debug(f"Detected intents: {intents}")
            except Exception as e:
                logger.error(f"Error in NLP processing: {str(e)}")
                return JsonResponse({
                    'message': 'Sorry, I had trouble understanding your message.',
                    'error': str(e)
                }, status=500)

            # Get shows based on detected genres
            shows = []
            try:
                # Check if the Show model has any data at all
                total_shows = Show.objects.count()
                logger.debug(f"Total shows in database: {total_shows}")

                if total_shows == 0:
                    logger.warning("No shows found in database!")
                    # Create a simple fallback response if database is empty
                    return JsonResponse({
                        'message': "I'd like to recommend some movies, but my database seems to be empty. Please make sure to populate the database with movies first.",
                        'recommendations': []
                    })

                if genres:
                    genre_filter = Q()
                    for genre in genres:
                        genre_filter |= Q(genre__icontains=genre)

                    # Get a pool of matching shows and randomly select from them
                    matching_shows = Show.objects.filter(genre_filter)
                    if matching_shows.count() > 3:
                        # If we have enough matches, mix top rated with random
                        top_genre_shows = list(matching_shows.order_by('-rating')[:5])
                        random_genre_shows = list(matching_shows.order_by('?')[:5])
                        # Combine, remove duplicates, and take first 3
                        combined_shows = list({show.id: show for show in top_genre_shows + random_genre_shows}.values())
                        shows = combined_shows[:3]
                    else:
                        # If few matches, just take what we have
                        shows = matching_shows.order_by('-rating')[:3]

                # If no shows found or no genres detected, get some default shows
                if not shows:
                    total_shows = Show.objects.count()
                    if total_shows > 10:
                        # Get a mix of top-rated and random shows
                        top_shows = list(Show.objects.all().order_by('-rating')[:5])
                        random_shows = list(Show.objects.all().order_by('?')[:5])
                        # Combine, remove duplicates, and take first 3
                        combined_shows = list({show.id: show for show in top_shows + random_shows}.values())
                        shows = combined_shows[:3]
                    else:
                        # Just use top rated if we don't have many shows
                        shows = Show.objects.all().order_by('-rating')[:3]
                    logger.debug(f"Using default shows, found {len(shows)}")

                logger.debug(f"Shows found: {[show.title for show in shows]}")
            except Exception as e:
                logger.error(f"Error fetching shows: {str(e)}")
                return JsonResponse({
                    'message': 'Sorry, I had trouble finding movie recommendations for you.',
                    'error': str(e)
                }, status=500)

            # Generate response
            try:
                response = chatbot.generate_response(user_message, shows)
                logger.debug(f"Generated response: {response}")
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                return JsonResponse({
                    'message': 'Sorry, I had trouble generating a response.',
                    'error': str(e)
                }, status=500)

            # Save bot message
            try:
                ChatMessage.objects.create(message=response['message'], is_bot=True)
                logger.debug("Saved bot response to database")
            except Exception as e:
                logger.error(f"Error saving bot message: {str(e)}")
                # Continue even if saving fails

            try:
                json_response = {
                    'message': response['message'],
                    'recommendations': [
                        {
                            'title': show.title,
                            'genre': show.genre,
                            'rating': show.rating,
                            'description': show.description,
                            'poster_url': show.get_poster_url() if hasattr(show, 'get_poster_url') else None
                        } for show in shows
                    ] if response.get('requires_recommendation', False) else []
                }
                logger.debug(
                    f"Prepared JSON response with {len(json_response.get('recommendations', []))} recommendations")
                return JsonResponse(json_response)
            except Exception as e:
                logger.error(f"Error preparing JSON response: {str(e)}")
                return JsonResponse({
                    'message': 'Sorry, there was an error processing your request.',
                    'error': str(e)
                }, status=500)

        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error in chat_message view: {str(e)}")
            logger.exception("Exception details:")
            return JsonResponse({
                'message': 'Sorry, there was an unexpected error processing your request.',
                'error': str(e)
            }, status=500)

    logger.warning(f"Invalid request method: {request.method}")
    return JsonResponse({
        'message': 'Sorry, this endpoint only accepts POST requests.',
        'error': 'Invalid request method'
    }, status=405)


def populate_database(request):
    """Admin function to populate the database with initial movie data including posters"""
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

                        # Get poster path
                        poster_path = details.get('poster_path')

                        # Create new show if it doesn't exist
                        if not Show.objects.filter(title=details['title']).exists():
                            Show.objects.create(
                                title=details['title'],
                                genre=genres,
                                rating=details['vote_average'],
                                description=details['overview'],
                                poster_path=poster_path
                            )
                            count += 1
                        # If it exists but doesn't have a poster, update it
                        elif poster_path:
                            show = Show.objects.get(title=details['title'])
                            if not show.poster_path:
                                show.poster_path = poster_path
                                show.save()

            return JsonResponse({'success': True, 'message': f'Added {count} movies to database'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)


def chat_history(request):
    """View to display the chat history"""
    messages = ChatMessage.objects.all().order_by('timestamp')
    return render(request, 'chatbot/history.html', {'messages': messages})


@csrf_exempt
def check_db_status(request):
    """Debug endpoint to check database status"""
    try:
        show_count = Show.objects.count()
        chat_count = ChatMessage.objects.count()

        recent_shows = Show.objects.all().order_by('-id')[:5]
        recent_chats = ChatMessage.objects.all().order_by('-timestamp')[:5]

        show_data = [
            {
                'id': show.id,
                'title': show.title,
                'genre': show.genre,
                'rating': show.rating
            }
            for show in recent_shows
        ]

        chat_data = [
            {
                'id': chat.id,
                'message': chat.message[:50] + '...' if len(chat.message) > 50 else chat.message,
                'is_bot': chat.is_bot,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for chat in recent_chats
        ]

        return JsonResponse({
            'status': 'success',
            'database': {
                'show_count': show_count,
                'chat_message_count': chat_count,
                'recent_shows': show_data,
                'recent_chats': chat_data
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error checking database: {str(e)}'
        }, status=500)


@csrf_exempt
def simple_chat(request):
    """A simplified chat endpoint that doesn't rely on the database or NLP"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()

            # Simple pattern matching for responses
            response = "I'm not sure how to respond to that. Could you ask me about movies?"
            recommendations = []

            # Simple movie data
            movies = [
                {
                    'title': 'The Shawshank Redemption',
                    'genre': 'Drama',
                    'rating': 9.3,
                    'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'
                },
                {
                    'title': 'The Godfather',
                    'genre': 'Crime, Drama',
                    'rating': 9.2,
                    'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.'
                },
                {
                    'title': 'The Dark Knight',
                    'genre': 'Action, Crime, Drama',
                    'rating': 9.0,
                    'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.'
                },
                {
                    'title': 'Pulp Fiction',
                    'genre': 'Crime, Drama',
                    'rating': 8.9,
                    'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'
                },
                {
                    'title': 'The Matrix',
                    'genre': 'Action, Sci-Fi',
                    'rating': 8.7,
                    'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.'
                }
            ]

            # Check for greeting
            if any(word in user_message for word in ['hi', 'hello', 'hey', 'greetings']):
                response = "Hello! I'm your movie recommendation assistant. What kind of movies do you enjoy watching?"

            # Check for comedy
            elif 'comedy' in user_message:
                response = "Here are some comedy movies you might enjoy:"
                recommendations = [movies[3]]  # Pulp Fiction has dark comedy elements

            # Check for action
            elif 'action' in user_message:
                response = "Here are some action movies you might enjoy:"
                recommendations = [movies[2], movies[4]]  # Dark Knight and Matrix

            # Check for drama
            elif 'drama' in user_message:
                response = "Here are some drama movies you might enjoy:"
                recommendations = [movies[0], movies[1]]  # Shawshank and Godfather

            # Check for top rated
            elif 'top' in user_message or 'best' in user_message or 'highest' in user_message:
                response = "Here are some of the highest rated movies of all time:"
                recommendations = movies[:3]  # Top 3 movies

            # Generic inquiry about movies
            elif 'movie' in user_message or 'recommend' in user_message or 'suggestion' in user_message:
                response = "Here are some movie recommendations for you:"
                import random
                recommendations = random.sample(movies, min(3, len(movies)))

            # Save the interaction to the database if possible
            try:
                ChatMessage.objects.create(message=user_message, is_bot=False)
                ChatMessage.objects.create(message=response, is_bot=True)
            except Exception:
                # Ignore database errors
                pass

            return JsonResponse({
                'message': response,
                'recommendations': [
                    {
                        'title': movie['title'],
                        'genre': movie['genre'],
                        'rating': movie['rating'],
                        'description': movie['description']
                    } for movie in recommendations
                ]
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'message': 'Sorry, I couldn\'t understand your request.',
                'recommendations': []
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': f'Sorry, there was an error processing your request: {str(e)}',
                'recommendations': []
            }, status=500)

    return JsonResponse({
        'message': 'This endpoint only accepts POST requests.',
        'recommendations': []
    }, status=405)
