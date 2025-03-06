from django.db import models


class Show(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    rating = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:50]}"