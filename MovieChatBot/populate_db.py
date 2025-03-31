# Create a file called populate_db.py in your project root directory

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MovieChatBot.settings')
django.setup()

from chatbot.models import Show
from chatbot.tmdb_client import TMDBClient


def populate_database():
    """Populate the database with initial movie data from TMDB"""
    print("Starting database population...")

    # Clear existing data
    existing_count = Show.objects.count()
    print(f"Found {existing_count} existing shows in database")

    # Initialize TMDB client
    tmdb_client = TMDBClient()

    # Get popular movies from TMDB
    popular_movies = tmdb_client.get_popular_movies(page=1)
    count = 0

    if popular_movies and 'results' in popular_movies:
        print(f"Found {len(popular_movies['results'])} movies from TMDB API")

        for movie in popular_movies['results']:
            try:
                # Get more details about the movie
                details = tmdb_client.get_movie_details(movie['id'])

                if details:
                    # Extract genres
                    genres = ', '.join([genre['name'] for genre in details.get('genres', [])])

                    # Create new show if it doesn't exist
                    if not Show.objects.filter(title=details['title']).exists():
                        show = Show.objects.create(
                            title=details['title'],
                            genre=genres,
                            rating=details['vote_average'],
                            description=details['overview']
                        )
                        print(f"Added: {show.title} ({genres}) - Rating: {show.rating}")
                        count += 1
                    else:
                        print(f"Skipped (already exists): {details['title']}")
            except Exception as e:
                print(f"Error processing movie {movie.get('title', movie.get('id', 'unknown'))}: {str(e)}")

    print(f"Database population complete. Added {count} new movies.")
    print(f"Total movies in database: {Show.objects.count()}")


def add_sample_data():
    """Add sample data if API is not available"""
    sample_movies = [
        {
            "title": "The Shawshank Redemption",
            "genre": "Drama",
            "rating": 9.3,
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
        },
        {
            "title": "The Godfather",
            "genre": "Crime, Drama",
            "rating": 9.2,
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."
        },
        {
            "title": "The Dark Knight",
            "genre": "Action, Crime, Drama",
            "rating": 9.0,
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."
        },
        {
            "title": "Pulp Fiction",
            "genre": "Crime, Drama",
            "rating": 8.9,
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption."
        },
        {
            "title": "The Lord of the Rings: The Return of the King",
            "genre": "Action, Adventure, Fantasy",
            "rating": 8.9,
            "description": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring."
        },
        {
            "title": "Forrest Gump",
            "genre": "Drama, Romance",
            "rating": 8.8,
            "description": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold through the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart."
        },
        {
            "title": "Inception",
            "genre": "Action, Adventure, Sci-Fi",
            "rating": 8.8,
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
        },
        {
            "title": "The Matrix",
            "genre": "Action, Sci-Fi",
            "rating": 8.7,
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."
        },
        {
            "title": "The Silence of the Lambs",
            "genre": "Crime, Drama, Thriller",
            "rating": 8.6,
            "description": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims."
        },
        {
            "title": "Parasite",
            "genre": "Drama, Thriller",
            "rating": 8.6,
            "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan."
        }
    ]

    count = 0
    for movie in sample_movies:
        if not Show.objects.filter(title=movie['title']).exists():
            Show.objects.create(**movie)
            count += 1
            print(f"Added sample movie: {movie['title']}")

    print(f"Added {count} sample movies")


if __name__ == "__main__":
    print("Starting script...")

    try:
        # Try to populate from API first
        populate_database()
    except Exception as e:
        print(f"Error using TMDB API: {str(e)}")
        print("Falling back to sample data...")
        add_sample_data()

    print("Script completed!")