from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    meal = models.ForeignKey('api.Meal', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    portions = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    plates = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    special_instructions = models.TextField(blank=True)
    
    @property
    def total_price(self):
        return self.meal.price * self.quantity * self.portions * self.plates

    def __str__(self):
        return f"{self.quantity}x{self.portions}p{self.plates}pl {self.meal.name}"

    class Meta:
        unique_together = ['cart', 'meal'] 