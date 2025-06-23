from django.core.management.base import BaseCommand
from api.models import Meal, DeliveryType, Location
from django.core.files import File
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize the database with sample data'

    def handle(self, *args, **kwargs):
        # Create delivery types
        delivery_types = [
            {'name': 'Express Delivery', 'price': 300},
            {'name': 'Normal Delivery', 'price': 200}
        ]
        for dt in delivery_types:
            DeliveryType.objects.get_or_create(name=dt['name'], defaults={'price': dt['price']})
            self.stdout.write(self.style.SUCCESS(f'Created delivery type: {dt["name"]}'))

        # Create locations
        locations = [
            'EDC Hostel',
            'Amethyst',
            'SST',
            'SMC',
            'Coperative',
            'Faith',
            'Pod Living'
        ]
        for loc in locations:
            Location.objects.get_or_create(name=loc)
            self.stdout.write(self.style.SUCCESS(f'Created location: {loc}'))

        # Create meals
        meals = [
            {
                'name': 'Jollof Rice',
                'description': 'Delicious Nigerian-style jollof rice with chicken and vegetables',
                'price': 2500,
            },
            {
                'name': 'Fried Rice',
                'description': 'Special fried rice with mixed vegetables and choice of protein',
                'price': 2500,
            },
            {
                'name': 'Pounded Yam',
                'description': 'Smooth pounded yam served with egusi soup',
                'price': 3000,
            },
            {
                'name': 'Amala',
                'description': 'Traditional amala served with ewedu and gbegiri soup',
                'price': 2500,
            },
            {
                'name': 'Eba',
                'description': 'Fresh eba served with okro soup',
                'price': 2000,
            },
            {
                'name': 'Semo',
                'description': 'Smooth semo served with egusi soup',
                'price': 2000,
            },
            {
                'name': 'Fufu',
                'description': 'Fresh fufu served with light soup',
                'price': 2500,
            },
            {
                'name': 'Beans',
                'description': 'Well-cooked beans with plantain',
                'price': 1500,
            },
            {
                'name': 'Yam Porridge',
                'description': 'Delicious yam porridge with fish',
                'price': 2000,
            },
            {
                'name': 'Rice and Beans',
                'description': 'Special rice and beans with plantain',
                'price': 2000,
            }
        ]

        # Create a default image for meals
        default_image_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'default_meal.jpg')
        if not os.path.exists(default_image_path):
            # Create a simple colored image as default
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 600), color='#f0f0f0')
            d = ImageDraw.Draw(img)
            d.text((400, 300), "No Image", fill='#666666')
            img.save(default_image_path)

        for meal_data in meals:
            meal, created = Meal.objects.get_or_create(
                name=meal_data['name'],
                defaults={
                    'description': meal_data['description'],
                    'price': meal_data['price'],
                    'is_available': True
                }
            )
            if created:
                with open(default_image_path, 'rb') as f:
                    meal.image.save(f"{meal_data['name']}.jpg", File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f'Created meal: {meal_data["name"]}')) 