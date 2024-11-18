from django.db import models


class Locations(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=200)
    categories = models.JSONField(default=list)
    lon = models.FloatField()
    lat = models.FloatField()
    prioritized = models.BooleanField(default=False)
    objects = models.Manager()


