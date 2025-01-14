from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    MyTokenObtainPairView,
    CustomTokenRefreshView,
    UserRegistration,
    PasswordReset,
    PasswordResetConfirm,
    ChangePassword

)

urlpatterns = [
path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
path('register/', UserRegistration.as_view(), name='user_register'),
path('login/', MyTokenObtainPairView.as_view(), name='user_login'),
    path('password-reset/', PasswordReset.as_view(), name='password_reset'),
    path('password-reset-confirm/<int:uid>/<str:token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password-reset-auth-user/', ChangePassword.as_view(), name='password_reset_auth_user'),


]