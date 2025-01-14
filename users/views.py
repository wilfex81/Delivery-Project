import os
import json
import requests

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    MyTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,

)
from .models import  User
from .utils.token_expiry import ExpiringPasswordResetTokenGenerator


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
    
class ChangePassword(APIView):
    """
    Allows authenticated users to change their password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle the POST request for changing the password.
        
        """
        serializer = ChangePasswordSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Password changed successfully.")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordReset(APIView):
    """
    Handles sending a password reset email.
    """

    def post(self, request):
        """
        Sends a password reset email to the provided email if the user exists.

        Args:
            request: HTTP request containing the email.

        Returns:
            Success response regardless of whether the email exists in the system.
        """
        email = request.data.get('email')
        if not email:
            return Response({"error": _("Email is required")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": _("If an account exists with this email, a password reset link will be sent.")}, status=status.HTTP_200_OK)

        token_generator = ExpiringPasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_url = f"songaai://reset-password/?uid={uid}&token={token}"

        email_subject = _("Password Reset Request")
        html_content = render_to_string(
            'password_reset_email.html',
            {
                'user': user,
                'reset_url': reset_url,
                'current_year': timezone.now().year
            }
        )
        plain_text_content = render_to_string(
            'password_reset_email.txt',
            {
                'user': user,
                'reset_url': reset_url,
                'current_year': timezone.now().year
            }
        )

        email = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_text_content,
            from_email='test@gmail.com',
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")

        email.send()

        return Response({"message": _("If an account exists, a password reset link will be sent.")}, status=status.HTTP_200_OK)

class PasswordResetConfirm(APIView):
    """
    Handles setting the new password after confirming the reset token
    """
    def post(self, request, *args, **kwargs):
        """
        Validate the token shared with the url in the password reset api along with receiving the new password. 

        Args:
            request: The HTTP request containing the new password(password 1 and password 2)

        Returns:
            Response indicating password reset status
        """
        uidb64 = kwargs.get('uid')
        token = kwargs.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user or token"}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = ExpiringPasswordResetTokenGenerator()
        
        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        
        serializer = PasswordResetSerializer(data = {'new_password':password1, 'confirm_password':password2})
        
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password1)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)