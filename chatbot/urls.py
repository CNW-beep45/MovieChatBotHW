from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat_message, name='chat_message'),
    path('history/', views.chat_history, name='chat_history'),
    path('admin/populate/', views.populate_database, name='populate_database'),
]