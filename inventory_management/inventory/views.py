from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.urls import path
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Item
from .serializers import ItemSerializer, UserSerializer
from django.core.cache import cache
import logging
from rest_framework.permissions import IsAuthenticated

# Create your views here.

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {serializer.data['username']} registered")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            logger.info(f"User {username} logged in")
            serializer = TokenObtainPairSerializer.get_token(user)
            return Response({
                'username': user.username,
                'access': str(serializer.access_token),
                'refresh': str(serializer),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ItemView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Item {serializer.data['name']} created")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, item_id=None):
        if item_id:
            cached_item = cache.get(f'item_{item_id}')
            if cached_item:
                logger.info(f"Cache hit for item {item_id}")
                print(f"Cache hit for item {item_id}")  
                return Response(cached_item, status=status.HTTP_200_OK)

            try:
                print(f"Item {item_id} not found in cache. Fetching from database...")  
                item = Item.objects.get(pk=item_id)
                serializer = ItemSerializer(item)
                cache.set(f'item_{item_id}', serializer.data, timeout=60 * 5)
                logger.info(f"Item {item_id} retrieved and cached")
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                print(f"Item {item_id} does not exist.")  
                return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def put(self, request, item_id):
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            print(f"Item {item_id} not found for update.")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Invalidate the cache for the updated item
            cache.delete(f'item_{item_id}')  
            logger.info(f"Item {item_id} updated successfully")
            print(f"Item {item_id} updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)

        print(f"Update failed for item {item_id}: {serializer.errors}") 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
            cache.delete(f'item_{item_id}')  
            logger.info(f"Item {item_id} deleted successfully")
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            print(f"Item {item_id} not found for deletion.")  # Debug print statement
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)