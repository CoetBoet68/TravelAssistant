from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models


@api_view(['GET'])
def events_available_list(request):
    events = models.EventsAvailable.objects.all().values()
    events_list = list(events)
    return Response(events_list, status=status.HTTP_200_OK)

