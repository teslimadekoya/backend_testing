from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
import stripe
from django.conf import settings
from rest_framework.filters import SearchFilter
from .models import (
    Meal, Order, OrderItem, DeliveryType, 
    Location, GiftDetails, Cart, CartItem
)
from .serializers import (
    MealSerializer, OrderSerializer, DeliveryTypeSerializer,
    LocationSerializer, CartSerializer, CartItemSerializer
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

stripe.api_key = settings.STRIPE_SECRET_KEY

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class MealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meal.objects.filter(is_available=True)
    serializer_class = MealSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

class DeliveryTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    permission_classes = [permissions.AllowAny]

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def create(self, request):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            meal_id = serializer.validated_data['meal_id']
            quantity = serializer.validated_data.get('quantity', 1)
            portions = serializer.validated_data.get('portions', 1)
            plates = serializer.validated_data.get('plates', 1)
            special_instructions = serializer.validated_data.get('special_instructions', '')
            
            try:
                # Update existing cart item if it exists
                cart_item = CartItem.objects.get(cart=cart, meal_id=meal_id)
                cart_item.quantity = quantity
                cart_item.portions = portions
                cart_item.plates = plates
                cart_item.special_instructions = special_instructions
                cart_item.save()
            except CartItem.DoesNotExist:
                # Create new cart item if it doesn't exist
                CartItem.objects.create(
                    cart=cart,
                    meal_id=meal_id,
                    quantity=quantity,
                    portions=portions,
                    plates=plates,
                    special_instructions=special_instructions
                )
            
            # Return the updated cart data
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        cart = self.get_object()
        try:
            cart_item = cart.items.get(id=pk)
            serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Only update the fields that were provided
                if 'quantity' in serializer.validated_data:
                    cart_item.quantity = serializer.validated_data['quantity']
                if 'portions' in serializer.validated_data:
                    cart_item.portions = serializer.validated_data['portions']
                if 'plates' in serializer.validated_data:
                    cart_item.plates = serializer.validated_data['plates']
                if 'special_instructions' in serializer.validated_data:
                    cart_item.special_instructions = serializer.validated_data['special_instructions']
                
                cart_item.save()
                return Response(self.get_serializer(cart).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        cart = self.get_object()
        try:
            cart_item = cart.items.get(id=pk)
            cart_item.delete()
            return Response(self.get_serializer(cart).data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response(
                {'error': 'Cannot create order with empty cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total amount
        cart_total = cart.total_amount
        delivery_type = get_object_or_404(DeliveryType, id=request.data.get('delivery_type_id'))
        total_amount = cart_total + delivery_type.price

        try:
            # Create order
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(
                user=request.user,
                total_amount=total_amount,
                status='pending'  # Set initial status
            )

            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    meal=cart_item.meal,
                    quantity=cart_item.quantity,
                    portions=cart_item.portions,
                    plates=cart_item.plates,
                    special_instructions=cart_item.special_instructions,
                    unit_price=cart_item.meal.price,
                    total_price=cart_item.total_price
                )

            # Clear the cart
            cart.items.all().delete()

            return Response({
                'order': serializer.data,
                'message': 'Order created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        order.status = 'paid'
        order.save()
        return Response({'status': 'Payment confirmed'})
