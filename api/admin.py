from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Meal, Order, OrderItem, DeliveryType,
    Location, GiftDetails, Cart, CartItem, UserProfile
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('name', 'description')
    list_editable = ('is_available', 'price')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    list_editable = ('price',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(GiftDetails)
class GiftDetailsAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'recipient_matric_number', 'whatsapp_number')
    search_fields = ('recipient_name', 'recipient_matric_number')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    raw_id_fields = ('meal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at', 'is_gift')
    list_filter = ('status', 'delivery_type', 'is_gift')
    search_fields = ('user__username', 'user__email', 'gift_details__recipient_name')
    inlines = [OrderItemInline]
    readonly_fields = ('payment_intent_id', 'total_amount', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'gift_details')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ('meal',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

admin.site.register(UserProfile)
