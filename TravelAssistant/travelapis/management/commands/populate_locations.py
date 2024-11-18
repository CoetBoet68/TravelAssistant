from django.core.management.base import BaseCommand
from django.db import IntegrityError
from travelapis.models import Locations
import environ
import requests

def api_request(category):
    env = environ.Env()
    environ.Env.read_env()
    api_key = env("PLACES_KEY")
    filter_value = env("PLACES_FILTER")

    if not api_key or not filter_value:
        raise ValueError("Missing PLACES_KEY or PLACES_FILTER environment variables")

    base_url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": category,
        "filter": filter_value,
        "limit": 50,
        "apiKey": api_key
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": f"No places found for category '{category}'"}
        elif response.status_code == 400:
            return {"error": "Bad Request. Please check your input parameters"}
        else:
            return {"error": f"Unexpected error occurred: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Geoapify API: {str(e)}"}

class Command(BaseCommand):
    help = 'Script for populating locations'
    def handle(self, *args, **options):
        with open('travelapis/management/commands/categories.txt', 'r') as f:
            categories = f.read().splitlines()
            f.close()

        for category in categories:
            response = api_request(category)
            if "error" in response:
                self.stdout.write(
                    self.style.ERROR(f"Error fetching data for category '{category}': {response['error']}"))
                continue

            features = response.get("features", [])
            for feature in features:
                properties = feature.get("properties", {})
                try:
                    Locations.objects.create(
                        id=properties.get("place_id"),
                        name=properties.get("name"),
                        lon=properties.get("lon"),
                        lat=properties.get("lat"),
                        address=properties.get("formatted"),
                        categories=properties.get("categories", [])
                    )
                except IntegrityError as e:
                    print(f"Location {properties.get('name')} already exists")
            self.stdout.write(self.style.SUCCESS(f"Successfully populated data for category: {category}"))
