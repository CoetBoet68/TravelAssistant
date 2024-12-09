from django.db import models
import json

from rest_framework import serializers


def getHoursOpen(hours):
    weekday_hours = []
    weekend_hours = []
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekends = ["Saturday", "Sunday"]

    if hours:
        for entry in hours:
            day, time = entry.split(": ", 1)
            if day in weekdays:
                weekday_hours.append(time.replace(" ", "").lower())
            elif day in weekends:
                weekend_hours.append(time.replace(" ", "").lower())

    return {
        "weekday_hours": weekday_hours,
        "weekend_hours": weekend_hours,
    }

def getCategories(categoryList):
    categories = []
    if categoryList:
        for category in categoryList:
            categories.append(category.split('.')[-1])
    return categories

class LocationManager(models.Manager):
    def get_all(self):
        return Locations.objects.all().values()

    def check_unique(self, name, address):
        matches = list(Locations.objects.filter(name=name, address=address))
        if len(matches) > 0:
            return False
        return True

    def filter_search(self, filterObject):
        querySet = Locations.objects.all().order_by('-prioritized')
        filters = filterObject.get('baseFilters', {})
        if filters.get('name'):
            querySet = querySet.filter(name__icontains=filters.get('name'))

        if filters.get('address'):
            querySet = querySet.filter(address__icontains=filters.get('address'))

        if filters.get('prioritized'):
            querySet = querySet.filter(prioritized=filters.get('prioritized'))

        if filters.get('rating'):
            querySet = querySet.filter(rating__gt=filters.get('rating'))

        if filters.get('priceMin'):
            querySet = querySet.filter(priceMin__lte=filters.get('priceMin'))

        if filters.get('priceMax'):
            querySet = querySet.filter(priceMax__gte=filters.get('priceMax'))

        if filters.get('priceLevel'):
            querySet = querySet.filter(priceLevel__contains=filters.get('priceLevel').upper())

        if filters.get('goodForGroups'):
            querySet = querySet.filter(goodForGroups=filters.get('goodForGroups'))

        if filters.get('goodForChildren'):
            querySet = querySet.filter(goodForChildren=filters.get('goodForChildren'))

        if filters.get('allowsDogs'):
            querySet = querySet.filter(allowsDogs=filters.get('allowsDogs'))

        if filters.get('weekdayHours') or filters.get('weekendHours') or filters.get('category'):
            filteredList = []
            for entry in querySet:
                openHours = getHoursOpen(entry.hours)
                categories = getCategories(entry.categories)
                if filters.get('weekdayHours') and not filters.get('weekdayHours') in openHours['weekday_hours']:
                    continue

                if filters.get('weekendHours') and not filters.get('weekendHours') in openHours['weekend_hours']:
                    continue

                if filters.get('category') and not filters.get('category') in categories:
                    continue
                filteredList.append(entry)
            return LocationsSerializer(filteredList, many=True).data

        return LocationsSerializer(querySet, many=True).data

    def update_priority(self, body):
        if Locations.objects.get(id=body.get("id")):
            Locations.objects.filter(id=body.get("id")).update(prioritized=body.get("prioritized"))
            return LocationsSerializer(Locations.objects.get(id=body.get("id"))).data
        return None

    def returnLLMResults(self, list):
        locations = Locations.objects.filter(id__in=list)
        return LocationsSerializer(locations, many=True).data

class Locations(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    address = models.CharField()
    categories = models.JSONField(default=list)
    categories_text = models.TextField(blank=True, null=True)
    lon = models.FloatField()
    lat = models.FloatField()
    prioritized = models.BooleanField(default=False)
    rating = models.FloatField(null=True)
    hours = models.JSONField(default=list, null=True)
    hours_text = models.TextField(blank=True, null=True)
    priceLevel = models.CharField(max_length=255, null=True)
    priceMin = models.IntegerField(null=True)
    priceMax = models.IntegerField(null=True)
    allowsDogs = models.BooleanField(null=True)
    goodForGroups = models.BooleanField(null=True)
    goodForChildren = models.BooleanField(null=True)
    objects = LocationManager()

class LocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'


