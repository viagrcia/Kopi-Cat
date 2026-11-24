import requests
import time
from django.core.management.base import BaseCommand
from cafes.models import Cafe

class Command(BaseCommand):
    help = 'Removes cafes that fall outside of Malolos borders'

    def handle(self, *args, **kwargs):
        self.stdout.write("Scanning database for out-of-bounds cafes (this takes a moment)...")
        
        cafes = Cafe.objects.all()
        deleted_count = 0
        
        for cafe in cafes:
            # Protect your manually added test cafe so it doesn't get wiped!
            if cafe.name == "Honey Bakes Cafe":
                continue
                
            url = f"https://nominatim.openstreetmap.org/reverse?lat={cafe.latitude}&lon={cafe.longitude}&format=json"
            headers = {'User-Agent': 'KopiCat-Malolos-Directory/1.0'}
            
            try:
                response = requests.get(url, headers=headers).json()
                address = response.get('address', {})
                
                # Convert the entire address dictionary to a string to easily search for 'Malolos'
                address_string = str(address.values())
                
                # If 'Malolos' is nowhere in the official address data, delete it from the database
                if 'Malolos' not in address_string:
                    self.stdout.write(self.style.WARNING(f"Deleting {cafe.name}... (Not in Malolos)"))
                    cafe.delete()
                    deleted_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Skipped {cafe.name} due to API error."))
            
            # The API requires a 1.5-second delay between checks so we don't get blocked
            time.sleep(1.5) 
            
        self.stdout.write(self.style.SUCCESS(f"Cleaned up! Removed {deleted_count} out-of-bounds cafes."))