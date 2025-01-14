import os
import json
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    MyTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    UserSerializer

)

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Generates access and refresh token when a user logs in
    """
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    """
    Generates a custom refersh token when an expiring access token is passed in the params
    """
    serializer_class = CustomTokenRefreshSerializer

class UserRegistration(APIView):
    """
    Handles User registration
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

