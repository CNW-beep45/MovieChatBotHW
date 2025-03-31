# Update your models.py file to add a poster_path field

from django.db import models


class Show(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    rating = models.FloatField()
    description = models.TextField()
    poster_path = models.CharField(max_length=255, null=True, blank=True)  # Added field for movie poster

    def __str__(self):
        return self.title

    def get_poster_url(self):
        """Get the full URL for the movie poster"""
        if self.poster_path:
            base_url = "https://image.tmdb.org/t/p/w500"
            return f"{base_url}{self.poster_path}"
        return None  # Return None if no poster is available


class ChatMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:50]}"