from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models


@api_view(['GET'])
def locations_list(request):
    locations = list(models.Locations.objects.all().values())
    return Response(locations, status=status.HTTP_200_OK)

