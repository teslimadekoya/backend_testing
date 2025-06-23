from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import requests
import json
import os
from .models import UserProfile
from rest_framework import parsers

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password1') or request.data.get('password')
        if not username or not email or not password:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'You already have an account with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Automatically log them in and generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'message': 'Account created successfully! Welcome to North Café!'
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = None
        
        # Try to authenticate with email first
        if email:
            try:
                # Find user by email
                user_obj = User.objects.get(email=email)
                # Authenticate with username and password
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        # If email login failed, try username login
        if user is None and username:
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'username': user.username, 'email': user.email}
            })
        
        # Check if user exists at all
        user_exists = False
        if email:
            user_exists = User.objects.filter(email=email).exists()
        if username and not user_exists:
            user_exists = User.objects.filter(username=username).exists()
            
        if not user_exists:
            return Response({'error': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'})

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({'username': user.username, 'email': user.email})

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            return Response({
                'uid': uid,
                'token': token
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'No account found with this email'
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        
        if not all([uid, token, password]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Decode the user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Verify the token
            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if new password is same as current password
            if user.check_password(password):
                return Response({'error': 'New password cannot be the same as your current password'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the password
            user.set_password(password)
            user.save()
            
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
            
        except (TypeError, ValueError, User.DoesNotExist):
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    def post(self, request):
        user = request.user
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        old_password = request.data.get('old_password', '').strip()
        new_password = request.data.get('new_password', '').strip()
        profile_image = request.FILES.get('profile_image')
        
        # Check if any fields are being updated
        is_updating_username = username != ''
        is_updating_email = email != ''
        is_updating_password = old_password != '' or new_password != ''
        is_updating_image = profile_image is not None
        
        if not any([is_updating_username, is_updating_email, is_updating_password, is_updating_image]):
            return Response({'error': 'No fields to update'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate and update username
        if is_updating_username:
            if len(username) < 3:
                return Response({'error': 'Username must be at least 3 characters long'}, status=status.HTTP_400_BAD_REQUEST)
            if not username.replace('_', '').isalnum():
                return Response({'error': 'Username can only contain letters, numbers, and underscores'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)
            user.username = username
        # Validate and update email
        if is_updating_email:
            if not email or '@' not in email:
                return Response({'error': 'Please enter a valid email address'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email
        # Validate and update password
        if is_updating_password:
            if not old_password:
                return Response({'error': 'Current password is required to change password'}, status=status.HTTP_400_BAD_REQUEST)
            if not new_password:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
            if len(new_password) < 8:
                return Response({'error': 'Password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(old_password):
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            if user.check_password(new_password):
                return Response({'error': 'New password cannot be the same as current password'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
        # Save the user
        try:
            user.save()
            # Handle profile image
            if is_updating_image:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.profile_image = profile_image
                profile.save()
            # Prepare response message
            updates = []
            if is_updating_username:
                updates.append('username')
            if is_updating_email:
                updates.append('email')
            if is_updating_password:
                updates.append('password')
            if is_updating_image:
                updates.append('profile image')
            message = f"Successfully updated {', '.join(updates)}"
            return Response({
                'message': message,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'profile_image': user.profile.profile_image.url if hasattr(user, 'profile') and user.profile.profile_image else None
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to update profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 