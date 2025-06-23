from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os
import requests
from api.models import Meal

class Command(BaseCommand):
    help = 'Delete all existing meals and add new ones with real food images'

    def handle(self, *args, **kwargs):
        # Delete all existing meals
        self.stdout.write('Deleting all existing meals...')
        Meal.objects.all().delete()
        
        # Define new meals with reliable food images
        meals_data = [
            {
                'name': 'Jollof Rice',
                'description': 'Delicious Nigerian-style jollof rice with chicken and vegetables',
                'price': 2500,
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Fried Rice',
                'description': 'Special fried rice with mixed vegetables and choice of protein',
                'price': 2500,
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Pounded Yam',
                'description': 'Smooth pounded yam served with egusi soup',
                'price': 3000,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Amala',
                'description': 'Traditional amala served with ewedu and gbegiri soup',
                'price': 2500,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Eba',
                'description': 'Fresh eba served with okro soup',
                'price': 2000,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Semo',
                'description': 'Smooth semo served with egusi soup',
                'price': 2000,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Fufu',
                'description': 'Fresh fufu served with light soup',
                'price': 2500,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Beans',
                'description': 'Well-cooked beans with plantain',
                'price': 1500,
                'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&h=600&fit=crop'
            },
            {
                'name': 'Yam Porridge',
                'description': 'Delicious yam porridge with fish',
                'price': 2000,
                'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop'
            },
            {
                'name': 'Rice and Beans',
                'description': 'Special rice and beans with plantain',
                'price': 2000,
                'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&h=600&fit=crop'
            }
        ]

        # Create meals directory if it doesn't exist
        meals_dir = os.path.join(settings.MEDIA_ROOT, 'meals')
        os.makedirs(meals_dir, exist_ok=True)

        # Reliable fallback image URLs
        fallback_images = [
            'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&h=600&fit=crop'
        ]

        for meal_data in meals_data:
            try:
                # Try multiple image URLs until one works
                image_downloaded = False
                image_urls_to_try = [meal_data['image_url']] + fallback_images
                
                for image_url in image_urls_to_try:
                    try:
                        response = requests.get(image_url, timeout=10)
                        if response.status_code == 200:
                            # Save image to local file
                            image_filename = f"{meal_data['name'].replace(' ', '_')}.jpg"
                            image_path = os.path.join(meals_dir, image_filename)
                            
                            with open(image_path, 'wb') as f:
                                f.write(response.content)
                            
                            # Create meal object
                            meal = Meal.objects.create(
                                name=meal_data['name'],
                                description=meal_data['description'],
                                price=meal_data['price'],
                                is_available=True
                            )
                            
                            # Save image to meal
                            with open(image_path, 'rb') as f:
                                meal.image.save(image_filename, File(f), save=True)
                            
                            self.stdout.write(
                                self.style.SUCCESS(f'Created meal: {meal_data["name"]} with image')
                            )
                            image_downloaded = True
                            break
                    except Exception as e:
                        continue
                
                if not image_downloaded:
                    # Create meal without image
                    meal = Meal.objects.create(
                        name=meal_data['name'],
                        description=meal_data['description'],
                        price=meal_data['price'],
                        is_available=True
                    )
                    self.stdout.write(
                        self.style.WARNING(f'Created meal: {meal_data["name"]} without image')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating meal {meal_data["name"]}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully reset all meals!')
        ) 