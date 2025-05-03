from rest_framework import serializers
from chatbot.models import Show, ChatMessage


class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = ['id', 'title', 'genre', 'rating', 'description']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'timestamp', 'is_bot']