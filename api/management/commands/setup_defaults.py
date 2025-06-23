from django.core.management.base import BaseCommand
from api.models import DeliveryType, Location

class Command(BaseCommand):
    help = 'Sets up default delivery types and locations'

    def handle(self, *args, **kwargs):
        # Create default delivery types
        regular, created = DeliveryType.objects.get_or_create(
            name='regular',
            defaults={'price': 500.00}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created regular delivery type'))
        
        express, created = DeliveryType.objects.get_or_create(
            name='express',
            defaults={'price': 1000.00}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created express delivery type'))

        # Create default locations
        locations = [
            'hall1', 'hall2', 'hall3', 'faculty_sci',
            'faculty_eng', 'faculty_arts', 'library', 'cafe'
        ]
        
        for loc in locations:
            location, created = Location.objects.get_or_create(name=loc)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created location: {loc}'))

        self.stdout.write(self.style.SUCCESS('Successfully set up all defaults')) 