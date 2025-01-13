from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView



path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
