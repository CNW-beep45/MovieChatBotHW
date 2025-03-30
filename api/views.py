from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
from chatbot.models import Show, ChatMessage
from .serializers import ShowSerializer, ChatMessageSerializer
from chatbot.utils import EnhancedChatBotNLP

chatbot = EnhancedChatBotNLP()


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to the Movie ChatBot API',
        'endpoints': {
            'shows': request.build_absolute_uri(reverse('show-list')),
            'recommendations': request.build_absolute_uri(reverse('recommendations')),
        }
    })


# Class-based view for shows
class ShowList(generics.ListAPIView):
    queryset = Show.objects.all().order_by('-rating')
    serializer_class = ShowSerializer

    def get_queryset(self):
        queryset = Show.objects.all().order_by('-rating')
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        return queryset


# Keep the function-based view temporarily as a fallback
@api_view(['GET'])
def show_list(request):
    shows = Show.objects.all().order_by('-rating')
    serializer = ShowSerializer(shows, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def recommendations(request):
    return Response({
        'message': 'Recommendations will appear here'
    })