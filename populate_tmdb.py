# Create a file called populate_tmdb.py in your project root directory

import os
import sys
import django
import time
import logging

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MovieChatBot.settings')
django.setup()

# Django imports
from chatbot.models import Show
from chatbot.tmdb_client import TMDBClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('populate_tmdb.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tmdb_populate')


def populate_from_popular(tmdb_client, pages=3):
    """Populate database with popular movies from multiple pages"""
    total_added = 0

    for page in range(1, pages + 1):
        logger.info(f"Fetching popular movies page {page}")
        popular_movies = tmdb_client.get_popular_movies(page=page)

        if not popular_movies or 'results' not in popular_movies:
            logger.error(f"Failed to get popular movies for page {page}")
            continue

        logger.info(f"Found {len(popular_movies['results'])} movies on page {page}")

        for movie in popular_movies['results']:
            try:
                # Get detailed movie information
                details = tmdb_client.get_movie_details(movie['id'])

                if not details:
                    logger.warning(f"Could not get details for movie ID {movie['id']}")
                    continue

                # Extract genres
                genres = ', '.join([genre['name'] for genre in details.get('genres', [])])

                # Skip adult content
                if details.get('adult', False):
                    logger.info(f"Skipping adult content: {details['title']}")
                    continue

                # Skip movies with no genre
                if not genres:
                    logger.info(f"Skipping movie with no genres: {details['title']}")
                    continue

                # Create new show if it doesn't exist
                if not Show.objects.filter(title=details['title']).exists():
                    Show.objects.create(
                        title=details['title'],
                        genre=genres,
                        rating=details['vote_average'],
                        description=details['overview'],
                        poster_path=details.get('poster_path')  # Added poster path
                    )
                    logger.info(f"Added: {details['title']} ({genres}) - Rating: {details['vote_average']}")
                    total_added += 1
                else:
                    # Update poster if it doesn't exist
                    existing_show = Show.objects.get(title=details['title'])
                    if not existing_show.poster_path and details.get('poster_path'):
                        existing_show.poster_path = details.get('poster_path')
                        existing_show.save()
                        logger.info(f"Updated poster for: {details['title']}")
                    else:
                        logger.info(f"Skipped (already exists): {details['title']}")

            except Exception as e:
                logger.error(f"Error processing movie {movie.get('title', movie.get('id', 'unknown'))}: {str(e)}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.25)

    return total_added


def populate_from_genres(tmdb_client):
    """Populate database with movies from specific genres"""
    # Get genre list
    genre_list = tmdb_client.get_genre_list()
    if not genre_list or 'genres' not in genre_list:
        logger.error("Failed to get genre list")
        return 0

    total_added = 0

    # Process each genre
    for genre in genre_list['genres']:
        genre_id = genre['id']
        genre_name = genre['name']

        logger.info(f"Processing genre: {genre_name}")

        # Get movies for this genre
        genre_movies = tmdb_client.discover_movies(genres=[genre_id], page=1)

        if not genre_movies or 'results' not in genre_movies:
            logger.error(f"Failed to get movies for genre {genre_name}")
            continue

        logger.info(f"Found {len(genre_movies['results'])} movies for genre {genre_name}")

        # Process each movie
        for movie in genre_movies['results'][:10]:  # Limit to 10 per genre to avoid too many API calls
            try:
                # Get detailed movie information
                details = tmdb_client.get_movie_details(movie['id'])

                if not details:
                    logger.warning(f"Could not get details for movie ID {movie['id']} in genre {genre_name}")
                    continue

                # Extract genres (there may be multiple)
                genres = ', '.join([g['name'] for g in details.get('genres', [])])

                # Skip adult content
                if details.get('adult', False):
                    logger.info(f"Skipping adult content: {details['title']}")
                    continue

                # Create new show if it doesn't exist
                if not Show.objects.filter(title=details['title']).exists():
                    Show.objects.create(
                        title=details['title'],
                        genre=genres,
                        rating=details['vote_average'],
                        description=details['overview']
                    )
                    logger.info(f"Added: {details['title']} ({genres}) - Rating: {details['vote_average']}")
                    total_added += 1
                else:
                    logger.info(f"Skipped (already exists): {details['title']}")

            except Exception as e:
                logger.error(f"Error processing movie {movie.get('title', movie.get('id', 'unknown'))}: {str(e)}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.25)

    return total_added


def populate_from_search(tmdb_client, search_terms):
    """Populate database with movies from specific search terms"""
    total_added = 0

    for term in search_terms:
        logger.info(f"Searching for: {term}")

        # Search for movies matching the term
        search_results = tmdb_client.search_movies(term)

        if not search_results or 'results' not in search_results:
            logger.error(f"Failed to get search results for {term}")
            continue

        logger.info(f"Found {len(search_results['results'])} results for '{term}'")

        # Process each movie (limit to top 5 results per search)
        for movie in search_results['results'][:5]:
            try:
                # Get detailed movie information
                details = tmdb_client.get_movie_details(movie['id'])

                if not details:
                    logger.warning(f"Could not get details for movie ID {movie['id']} from search '{term}'")
                    continue

                # Extract genres
                genres = ', '.join([genre['name'] for genre in details.get('genres', [])])

                # Skip adult content
                if details.get('adult', False):
                    logger.info(f"Skipping adult content: {details['title']}")
                    continue

                # Create new show if it doesn't exist
                if not Show.objects.filter(title=details['title']).exists():
                    Show.objects.create(
                        title=details['title'],
                        genre=genres,
                        rating=details['vote_average'],
                        description=details['overview']
                    )
                    logger.info(f"Added: {details['title']} ({genres}) - Rating: {details['vote_average']}")
                    total_added += 1
                else:
                    logger.info(f"Skipped (already exists): {details['title']}")

            except Exception as e:
                logger.error(f"Error processing movie {movie.get('title', movie.get('id', 'unknown'))}: {str(e)}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.25)

    return total_added


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
            logger.info(f"Added sample movie: {movie['title']}")

    logger.info(f"Added {count} sample movies")
    return count


if __name__ == "__main__":
    logger.info("Starting TMDB database population script...")

    # Initialize TMDB client
    tmdb_client = TMDBClient()

    # Get current database status
    existing_count = Show.objects.count()
    logger.info(f"Found {existing_count} existing shows in database")

    try:
        # Verify TMDB API connection
        test_response = tmdb_client.get_popular_movies(page=1)
        if not test_response or 'results' not in test_response:
            logger.error("Failed to connect to TMDB API. Check your API key and internet connection.")
            raise Exception("TMDB API connection failed")

        logger.info("Successfully connected to TMDB API")

        # Add popular movies
        popular_count = populate_from_popular(tmdb_client, pages=3)
        logger.info(f"Added {popular_count} popular movies")

        # Add genre-specific movies
        genre_count = populate_from_genres(tmdb_client)
        logger.info(f"Added {genre_count} genre-specific movies")

        # Add movies from specific searches
        search_terms = [
            "comedy", "sci-fi", "romance", "animated", "action",
            "thriller", "documentary", "fantasy", "horror", "musical"
        ]
        search_count = populate_from_search(tmdb_client, search_terms)
        logger.info(f"Added {search_count} movies from search terms")

        total_added = popular_count + genre_count + search_count
        logger.info(f"Total movies added from TMDB API: {total_added}")

    except Exception as e:
        logger.error(f"Error using TMDB API: {str(e)}")
        logger.info("Falling back to sample data...")
        sample_count = add_sample_data()
        logger.info(f"Added {sample_count} sample movies as fallback")

    final_count = Show.objects.count()
    logger.info(f"Database population complete. Total movies in database: {final_count}")