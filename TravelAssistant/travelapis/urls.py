from django.urls import path
from . import views

app_name = 'travel_apis'

urlpatterns = [
    path('locations/all', views.locations_list, name='locations_list'),
]