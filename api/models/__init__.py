from .meal import Meal
from .order import Order, OrderItem, DeliveryType, Location, GiftDetails
from .cart import Cart, CartItem
from django.db import models
from django.contrib.auth.models import User

__all__ = [
    'Meal',
    'Order',
    'OrderItem',
    'DeliveryType',
    'Location',
    'GiftDetails',
    'Cart',
    'CartItem',
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
