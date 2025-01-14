from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    MyTokenObtainPairView,
    CustomTokenRefreshView,

)

urlpatterns = [
path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
path('login/', MyTokenObtainPairView.as_view(), name='user_login'),


]