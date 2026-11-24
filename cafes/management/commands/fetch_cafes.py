import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cafes.models import Cafe

class Command(BaseCommand):
    help = 'Fetches ALL cafes in Malolos using a fast Bounding Box query'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching cafes using Bounding Box...")

        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # OPTIMIZED QUERY: Uses a geographic coordinate box around Malolos for instant processing
        overpass_query = """
        [out:json][timeout:25];
        (
          nwr["amenity"="cafe"](14.7844, 120.7663, 14.8824, 120.8647);
          nwr["shop"="coffee"](14.7844, 120.7663, 14.8824, 120.8647);
        );
        out center;
        """
        
        headers = {
            'User-Agent': 'KopiCat-Malolos-Directory/1.0 (Student IT Project)'
        }

        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"API Error: {response.status_code}"))
            return

        data = response.json()
        elements = data.get('elements', [])
        
        added_count = 0

        for element in elements:
            tags = element.get('tags', {})
            name = tags.get('name')
            
            if not name:
                continue

            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')
            
            if not lat or not lon:
                continue
            
            slug = slugify(name)
            
            if not Cafe.objects.filter(name=name).exists():
                Cafe.objects.create(
                    name=name,
                    slug=slug,
                    latitude=lat,
                    longitude=lon,
                    barangay='Malolos Area',
                    vibe_tags='Local Cafe, Coffee',
                    price_range='$$'
                )
                added_count += 1
                self.stdout.write(self.style.SUCCESS(f"Added: {name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully added {added_count} new cafes!"))