from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Meal, Order, OrderItem, DeliveryType, 
    Location, GiftDetails, Cart, CartItem, UserProfile
)

User = get_user_model()

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available']

class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = ['id', 'name', 'price']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']

class GiftDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftDetails
        fields = ['whatsapp_number', 'recipient_name', 'recipient_matric_number']

class CartItemSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    meal_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'meal', 'meal_id', 'quantity', 'portions', 'plates', 'special_instructions', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount']

class OrderItemSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'meal', 'quantity', 'portions', 'plates', 'special_instructions', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_type = DeliveryTypeSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    gift_details = GiftDetailsSerializer(required=False)
    delivery_type_id = serializers.IntegerField(write_only=True)
    location_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'items', 'delivery_type', 'delivery_type_id',
            'location', 'location_id', 'is_gift', 'gift_details',
            'status', 'total_amount', 'created_at'
        ]
        read_only_fields = ['status', 'total_amount']

    def create(self, validated_data):
        gift_details_data = validated_data.pop('gift_details', None)
        if gift_details_data and validated_data.get('is_gift'):
            gift_details = GiftDetails.objects.create(**gift_details_data)
            validated_data['gift_details'] = gift_details
        return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_image']

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image']
        read_only_fields = ['id'] 

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            request = self.context.get('request')
            url = obj.profile.profile_image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None 