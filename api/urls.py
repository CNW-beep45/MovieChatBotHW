from django.urls import path
from . import views

app_name = 'api'  # Add namespace to avoid conflicts

urlpatterns = [
    path('', views.api_root, name='api_root'),
]