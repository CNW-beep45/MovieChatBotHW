from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
    # Use the function-based view for now - easier to debug
    path('shows/', views.show_list, name='show-list'),
    # When ready to switch to class-based view, comment out the line above and uncomment below
    # path('shows/', views.ShowList.as_view(), name='show-list'),
    path('recommendations/', views.recommendations, name='recommendations'),
]