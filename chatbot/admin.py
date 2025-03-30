# Update chatbot/admin.py

from django.contrib import admin
from .models import Show, ChatMessage


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'rating')
    list_filter = ('genre', 'rating')
    search_fields = ('title', 'genre', 'description')
    ordering = ('-rating', 'title')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('get_truncated_message', 'is_bot', 'timestamp')
    list_filter = ('is_bot', 'timestamp')
    search_fields = ('message',)
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def get_truncated_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    get_truncated_message.short_description = 'Message'