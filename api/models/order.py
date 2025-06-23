from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator

User = get_user_model()

class DeliveryType(models.Model):
    DELIVERY_CHOICES = [
        ('regular', 'Regular'),  # Put regular first as it will be default
        ('express', 'Express'),
    ]
    name = models.CharField(max_length=10, choices=DELIVERY_CHOICES, unique=True, default='regular')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.get_name_display()

class Location(models.Model):
    LOCATION_CHOICES = [
        ('hall1', 'Hall 1'),  # First option will be default
        ('hall2', 'Hall 2'),
        ('hall3', 'Hall 3'),
        ('faculty_sci', 'Faculty of Science'),
        ('faculty_eng', 'Faculty of Engineering'),
        ('faculty_arts', 'Faculty of Arts'),
        ('library', 'University Library'),
        ('cafe', 'University Cafeteria'),
    ]
    name = models.CharField(max_length=20, choices=LOCATION_CHOICES, unique=True, default='hall1')
    
    def __str__(self):
        return self.get_name_display()

# Create default delivery types if they don't exist
def create_default_delivery_types():
    DeliveryType.objects.get_or_create(
        name='regular',
        defaults={'price': 500.00}  # Regular delivery price
    )
    DeliveryType.objects.get_or_create(
        name='express',
        defaults={'price': 1000.00}  # Express delivery price
    )

# Create default locations if they don't exist
def create_default_locations():
    for code, name in Location.LOCATION_CHOICES:
        Location.objects.get_or_create(name=code)

class GiftDetails(models.Model):
    whatsapp_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^0\d{10}$',
                message='WhatsApp number must be exactly 11 digits and start with 0'
            )
        ]
    )
    recipient_name = models.CharField(max_length=255)
    recipient_matric_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Matric number must contain only numbers'
            )
        ]
    )
    
    def __str__(self):
        return f"Gift for {self.recipient_name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, default=1)  # Default to first delivery type (regular)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, default=1)  # Default to first location (hall1)
    is_gift = models.BooleanField(default=False)
    gift_details = models.OneToOneField(GiftDetails, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_intent_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    meal = models.ForeignKey('api.Meal', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    portions = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    plates = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    special_instructions = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity * self.portions * self.plates
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x{self.portions}p{self.plates}pl {self.meal.name}" 