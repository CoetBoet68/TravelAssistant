from django.db import models

class EventsAvailable(models.Model):
    date = models.DateField(auto_now=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=100)
    objects = models.Manager()
