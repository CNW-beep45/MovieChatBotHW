import os
import django
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MovieChatBot.settings')
django.setup()

from chatbot.models import Show
from chatbot.tmdb_client import TMDBClient


def update_movie_posters():
    # Initialize TMDB client
    tmdb_client = TMDBClient()

    # Get all shows without posters
    shows_without_posters = Show.objects.filter(poster_path__isnull=True)
    total = shows_without_posters.count()

    print(f"Found {total} shows without posters")

    updated = 0

    for show in shows_without_posters:
        try:
            # Search for the movie
            search_results = tmdb_client.search_movies(show.title)

            if search_results and 'results' in search_results and search_results['results']:
                # Get the first result
                movie = search_results['results'][0]

                # Update poster path
                if movie.get('poster_path'):
                    show.poster_path = movie['poster_path']
                    show.save()
                    updated += 1
                    print(f"Updated poster for: {show.title}")
                else:
                    print(f"No poster found for: {show.title}")
            else:
                print(f"No search results for: {show.title}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.25)

        except Exception as e:
            print(f"Error updating poster for {show.title}: {str(e)}")

    print(f"Updated {updated} of {total} shows with posters")


if __name__ == "__main__":
    update_movie_posters()