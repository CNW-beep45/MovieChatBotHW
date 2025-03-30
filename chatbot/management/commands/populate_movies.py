from django.core.management.base import BaseCommand
from chatbot.models import Show


class Command(BaseCommand):
    help = 'Adds sample movie data to the database'

    def handle(self, *args, **options):
        sample_movies = [
            {
                'title': 'The Dark Knight',
                'genre': 'Action, Crime, Drama',
                'rating': 9.0,
                'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.'
            },
            {
                'title': 'Inception',
                'genre': 'Action, Adventure, Sci-Fi',
                'rating': 8.8,
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.'
            },
            {
                'title': 'Pulp Fiction',
                'genre': 'Crime, Drama',
                'rating': 8.9,
                'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'
            },
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
                'title': 'Detective Pikachu',
                'genre': 'Action, Adventure, Comedy, Mystery, Sci-Fi, Pokemon',
                'rating': 6.6,
                'description': 'In a world where people collect Pokémon to do battle, a boy comes across an intelligent talking Pikachu who seeks to be a detective.'
            },
            {
                'title': 'The Conjuring',
                'genre': 'Horror, Mystery, Thriller',
                'rating': 7.5,
                'description': 'Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse.'
            },
            {
                'title': 'Hereditary',
                'genre': 'Drama, Horror, Mystery, Thriller',
                'rating': 7.3,
                'description': 'A grieving family is haunted by tragic and disturbing occurrences after the death of their secretive grandmother.'
            },
            {
                'title': 'John Wick',
                'genre': 'Action, Crime, Thriller',
                'rating': 7.4,
                'description': 'An ex-hit-man comes out of retirement to track down the gangsters that killed his dog and took everything from him.'
            },
            {
                'title': 'Mad Max: Fury Road',
                'genre': 'Action, Adventure, Sci-Fi, Thriller',
                'rating': 8.1,
                'description': 'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.'
            },
        ]

        # Add movies to database if they don't exist
        count = 0
        for movie in sample_movies:
            if not Show.objects.filter(title=movie['title']).exists():
                Show.objects.create(**movie)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} movies'))