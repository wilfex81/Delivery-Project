import requests



from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.permissions import IsAuthenticated


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    MyTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,

)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
