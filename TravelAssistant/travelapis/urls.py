from django.urls import path
from . import views

app_name = 'travel_api'

urlpatterns = [
    path('events', views.events_available_list, name='events_available_list'),
]