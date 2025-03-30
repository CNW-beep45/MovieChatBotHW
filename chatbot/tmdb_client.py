import requests
import os
from django.conf import settings


class TMDBClient:
    def __init__(self):
        # Get API key from environment variable or settings
        self.api_key = os.environ.get('TMDB_API_KEY', 'your_api_key_here')
        self.base_url = 'https://api.themoviedb.org/3'

    def search_movies(self, query, page=1):
        """Search for movies by title"""
        endpoint = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'query': query,
            'page': page,
            'include_adult': False,
            'language': 'en-US'
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None

    def get_movie_details(self, movie_id):
        """Get detailed information about a specific movie"""
        endpoint = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'append_to_response': 'credits,videos,recommendations',
            'language': 'en-US'
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None

    def discover_movies(self, genres=None, sort_by='popularity.desc', page=1):
        """Discover movies by genre"""
        endpoint = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'sort_by': sort_by,
            'page': page,
            'include_adult': False,
            'language': 'en-US'
        }

        if genres:
            # Convert genre names to IDs if needed
            if isinstance(genres[0], str):
                genre_ids = self.get_genre_ids(genres)
                if genre_ids:
                    params['with_genres'] = ','.join(map(str, genre_ids))
            else:
                params['with_genres'] = ','.join(map(str, genres))

        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None

    def get_popular_movies(self, page=1):
        """Get popular movies"""
        endpoint = f"{self.base_url}/movie/popular"
        params = {
            'api_key': self.api_key,
            'page': page,
            'language': 'en-US'
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None

    def get_genre_list(self):
        """Get list of movie genres from TMDB"""
        endpoint = f"{self.base_url}/genre/movie/list"
        params = {
            'api_key': self.api_key,
            'language': 'en-US'
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None

    def get_genre_ids(self, genre_names):
        """Convert genre names to TMDB genre IDs"""
        genres = self.get_genre_list()
        if not genres:
            return []

        genre_map = {genre['name'].lower(): genre['id'] for genre in genres.get('genres', [])}
        genre_ids = []

        for name in genre_names:
            name_lower = name.lower()
            # Handle common variations
            if name_lower == 'sci-fi':
                name_lower = 'science fiction'

            if name_lower in genre_map:
                genre_ids.append(genre_map[name_lower])

        return genre_ids