from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Locations


@api_view(['GET'])
def locations_list(request):
    locations = list(Locations.objects.get_all())
    return Response(locations, status=status.HTTP_200_OK)

@api_view(['POST'])
def locations_filter_search(request):
    locations = Locations.objects.filter_search(request.data)
    if len(locations) > 0:
        return Response(locations[0:100], status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_location_priority(request):
    location = Locations.objects.update_priority(request.data)
    if location:
        return Response(location, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

