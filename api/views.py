from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to the Movie ChatBot API',
        'endpoints': {
            'shows': request.build_absolute_uri(reverse('show-list')),
            'recommendations': request.build_absolute_uri(reverse('recommendations')),
        }
    })

# Basic show list view
@api_view(['GET'])
def show_list(request):
    return Response({
        'message': 'List of shows will appear here'
    })

# Basic recommendations view
@api_view(['POST'])
def recommendations(request):
    return Response({
        'message': 'Recommendations will appear here'
    })