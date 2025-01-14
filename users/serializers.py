import phonenumbers

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings

from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'first_name',
            'middle_name',
            'last_name',
            'username',
            'business_name',
            'license_status',
            'passport_or_id',
            'role',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_admin': {'read_only': True},
            'is_active': {'read_only': True},
            'is_verified': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            business_name=validated_data['business_name'],
            license_status=validated_data['license_status'],
            passport_or_id=validated_data['passport_or_id'],
            role=validated_data['role'],
        )

        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.business_name = validated_data.get('business_name', instance.business_name)
        instance.license_status = validated_data.get('license_status', instance.license_status)
        instance.passport_or_id = validated_data.get('passport_or_id', instance.passport_or_id)
        instance.role = validated_data.get('role', instance.role)

        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
   

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom jwt auth token
    """    
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        # Check token rotation and blacklisting
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

        data = {'refresh': str(refresh)}
        
        user_id = refresh.get('user_id')


        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        access_token = AccessToken.for_user(user)

        access_token['phone'] = str(user.phone)
        access_token['email'] = str(user.email)
        access_token['business_name'] = str(user.business_name)
        access_token['first_name'] = str(user.first_name)
        access_token['middle_name'] = str(user.middle_name) if user.middle_name else ''
        access_token['last_name'] = str(user.last_name)
        access_token['username'] = str(user.username)
        access_token['license_status'] = str(user.license_status)
        access_token['role'] = user.role
        access_token['is_verified'] = user.is_verified
        
        data['access'] = str(access_token)

        return data   

     
# Custom token obtain pair serializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['phone'] = str(user.phone)
        token['email'] = str(user.email)
        token['business_name'] = str(user.business_name)
        token['first_name'] = str(user.first_name)
        token['middle_name'] = str(user.middle_name) if user.middle_name else ''
        token['last_name'] = str(user.last_name)
        token['username'] = str(user.username)
        token['license_status'] = str(user.license_status)
        token['role'] = str(user.role)
        token['is_verified'] = user.is_verified

        return token

    @staticmethod
    def validate_and_format_phone(phone_number):
        # Remove any non-numeric characters from the phone number
        phone_number = ''.join(filter(str.isdigit, phone_number))

        # If the phone number starts with '254', remove it
        if phone_number.startswith('254'):
            phone_number = phone_number[3:]

        # If the phone number starts with '0', remove the leading zero
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        # If the phone number starts with '7', prepend '+254'
        elif phone_number.startswith('7'):
            phone_number = '+254' + phone_number
        # If the phone number starts with '254', prepend '+'
        elif phone_number.startswith('254'):
            phone_number = '+' + phone_number
        else:
            raise ValueError('Invalid phone number format')

        # Attempt to parse the phone number
        parsed_phone = phonenumbers.parse(phone_number, None)

        # Check if the parsed phone number is valid
        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValueError('Invalid phone number')

        # Format the phone number in E.164 format
        formatted_phone_number = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)

        return formatted_phone_number

    def validate(self, attrs):
        email_or_phone = attrs.get('email')
        password = attrs.get('password')

        # Check if email_or_phone is a valid email address
        try:
            validate_email(email_or_phone)
            # If it's a valid email address, use it as the credential
            credentials = {'email': email_or_phone, 'password': password}
        except ValidationError:
            # If it's not a valid email address, assume it's a phone number
            # and filter the email using the phone number
            try:
                # Attempt to parse and validate the phone number
                valid_phone_number = self.validate_and_format_phone(email_or_phone)

                # Retrieve the user by the formatted phone number
                user = get_object_or_404(User, phone=valid_phone_number)
                credentials = {'email': user.email, 'password': password}
            except (phonenumbers.phonenumberutil.NumberParseException, User.DoesNotExist):
                raise serializers.ValidationError('Invalid credentials')

        return super().validate(credentials)
    

class ChangePasswordSerializer(serializers.Serializer):
    """
    Handles changing password for authenticated users
    """

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_new_password = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        """
        Validate that the current password is correct and the new password match.
        """
        user = self.context['request'].user
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if not user.check_password(current_password):
            raise serializers.ValidationError({"current_password": _("Current password is incorrect.")})

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"new_password": _("New passwords do not match.")})

        has_digit = False
        has_lower = False
        has_upper = False
        has_special = False

        for char in new_password:
            if has_digit and has_lower and has_upper and has_special:
                break
            if char.isdigit():
                has_digit = True
            elif char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char in '@$!%*?&':
                has_special = True

        if not has_digit:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one digit.")})
        if not has_lower:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one lowercase letter.")})
        if not has_upper:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one uppercase letter.")})
        if not has_special:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one special character (e.g. @$!%*?&).")})

        if new_password == new_password.lower() or new_password ==new_password.upper():
            raise serializers.ValidationError({"new_password": _("Password must contain both uppercase and lowercase letters.")})

        return attrs

    def save(self, **kwargs):
        """
        save the new password for the user
        """

        user = self.context['request'].user
        user.set_password(self.validate_data['new_password'])
        user.save()
        
            
class PasswordResetSerializer(serializers.Serializer):
    """
    Hand;es password reset at the login level
    """
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        """
        Validate the new passwords ensuring they actually meet the rerequirements
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({"new_password": _("New Passwords do not match")})

        has_digit  = False
        has_lower = False
        has_upper = False
        has_special = False

        for char in new_password:
            if has_digit  and has_lower and has_upper and has_special:
                break
            if char.isdigit():
                has_digit = True
            elif char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char in '@$!%*?&':
                has_special = True

        if not has_digit:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one digit.")})
        if not has_lower:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one lowercase letter.")})
        if not has_upper:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one uppercase letter.")})
        if not has_special:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one special character (e.g. @$!%*?&).")})

        if new_password == new_password.lower() or new_password == new_password.upper():
            raise serializers.ValidationError({"new_password": _("Password must contain both uppercase and lowercase letters.")})

        return attrs
        
class PasswordResetSerializer(serializers.Serializer):
    """
    Hand;es password reset at the login level
    """
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        """
        Validate the new passwords ensuring they actually meet the rerequirements
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({"new_password": _("New Passwords do not match")})

        has_digit  = False
        has_lower = False
        has_upper = False
        has_special = False

        for char in new_password:
            if has_digit  and has_lower and has_upper and has_special:
                break
            if char.isdigit():
                has_digit = True
            elif char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char in '@$!%*?&':
                has_special = True

        if not has_digit:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one digit.")})
        if not has_lower:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one lowercase letter.")})
        if not has_upper:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one uppercase letter.")})
        if not has_special:
            raise serializers.ValidationError({"new_password": _("Password must contain at least one special character (e.g. @$!%*?&).")})

        if new_password == new_password.lower() or new_password == new_password.upper():
            raise serializers.ValidationError({"new_password": _("Password must contain both uppercase and lowercase letters.")})

        return attrs
