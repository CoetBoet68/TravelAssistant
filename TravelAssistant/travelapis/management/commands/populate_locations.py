from django.core.management.base import BaseCommand
from django.db import IntegrityError
from travelapis.models import Locations
import environ
import requests

def places_api_request(category):
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
        "limit": 300,
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

def place_details(body, key):
    p_id = body["id"]

    details_url = f"https://places.googleapis.com/v1/places/{p_id}"
    details_parameters = {
        "key": key,
        "fields": "regularOpeningHours,rating,priceRange,priceLevel,allowsDogs,goodForGroups,goodForChildren"
    }

    try:
        response = requests.get(details_url, params=details_parameters)

        if response.status_code == 200:
            data = response.json()
            return {
                "rating": data.get("rating"),
                "hours": data.get("regularOpeningHours", {}).get("weekdayDescriptions"),
                "priceLevel": data.get("priceLevel"),
                "priceMin": data.get("priceRange", {}).get("startPrice", {}).get("units"),
                "priceMax": data.get("priceRange", {}).get("endPrice", {}).get("units"),
                "allowsDogs": data.get("allowsDogs"),
                "goodForGroups": data.get("goodForGroups"),
                "goodForChildren": data.get("goodForChildren")
            }
        else:
            print(f"No details Found for place ID: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Google API: {str(e)}"}

def place_retrieve(lat, lon):
    env = environ.Env()
    environ.Env.read_env()
    api_key = env("GOOGLE_KEY")

    if not api_key:
        raise ValueError("Missing GOOGLE API key from environment variables")

    nearby_url = "https://places.googleapis.com/v1/places:searchNearby"
    nearby_headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": f"{api_key}",
        "X-Goog-FieldMask": "places.id,places.displayName"
    }
    nearby_data = {
        "maxResultCount": 1,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lon
                },
                "radius": 25
            }
        }
    }

    try:
        response = requests.post(nearby_url, json=nearby_data, headers=nearby_headers)

        if response.status_code == 200:
            data = response.json()
            places = data.get("places", [])
            if isinstance(places, list) and len(places) > 0:
                place = places[0]
            else:
                print("No places found in the response.")
                return None
            return place_details(place, api_key)
        elif response.status_code == 404:
            print("No places found for lat and long coordinates")
            return None
        elif response.status_code == 400:
            print(f"Bad Request. {response.text}")
            return None
        else:
            print(f"Unexpected error occurred: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Google API: {str(e)}"}

class Command(BaseCommand):
    help = 'Script for populating locations'
    def handle(self, *args, **options):
        with open('travelapis/management/commands/categories.txt', 'r') as f:
            categories = f.read().splitlines()
            f.close()

        for category in categories:
            response = places_api_request(category)
            if "error" in response:
                self.stdout.write(
                    self.style.ERROR(f"Error fetching data for category '{category}': {response['error']}"))
                continue

            features = response.get("features", [])
            for feature in features:
                properties = feature.get("properties", {})
                if not Locations.objects.check_unique(properties.get("name"), properties.get("formatted")):
                    continue
                details = place_retrieve(properties.get("lat"), properties.get("lon"))
                try:
                    if details:
                        Locations.objects.create(
                            id=properties.get("place_id"),
                            name=properties.get("name"),
                            lon=properties.get("lon"),
                            lat=properties.get("lat"),
                            address=properties.get("formatted"),
                            categories=properties.get("categories", []),
                            rating = details.get("rating"),
                            hours = details.get("hours"),
                            priceLevel = details.get("priceLevel"),
                            priceMin = details.get("priceMin"),
                            priceMax = details.get("priceMax"),
                            allowsDogs = details.get("allowsDogs"),
                            goodForGroups = details.get("goodForGroups"),
                            goodForChildren = details.get("goodForChildren")
                        )
                    else:
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
