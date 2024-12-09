from django.urls import path
from . import views

app_name = 'travel_apis'

urlpatterns = [
    path('locations/llm', views.location_llm_search, name='locations_llm_search'),
    path('locations/all', views.locations_list, name='locations_list'),
    path('locations/filter-search', views.locations_filter_search, name='locations_filter_search'),
    path('locations/update-priority', views.update_location_priority, name='locations_update_priority'),
]