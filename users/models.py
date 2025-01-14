from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import uuid

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """
    use_in_migrations = True

    def create_user(self, email, phone, password=None, **extra_fields):
        """
        Creates and saves a new user with the given email, phone, and password.
        """
        if not email:
            raise ValueError('Email address must be provided')
        if not phone:
            raise ValueError('Phone number must be provided')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)  #hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Roles.ADMIN)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, phone, password, **extra_fields)
    
class User(AbstractBaseUser):
    """
    Custom user model representing a user of the application.
    """
    class Roles(models.TextChoices):
        """
        Roles Choices
        """
        ADMIN = 'Admin', 'Admin'
        CLIENT = 'Client', 'Client'
    
    class License(models.TextChoices):
        """
        License status choices(Available or not)
        """
        YES = 'Yes', 'Yes'
        NO = 'No', 'No'
        
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=150, unique=False)
    middle_name = models.CharField(max_length=150, unique=False, blank=True, null=True)
    last_name = models.CharField(max_length=150, unique=False)
    passport_or_id = models.CharField(max_length=36, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    role = models.CharField(max_length=50, choices=Roles.choices)
    license_status = models.CharField(max_length=50, choices=License.choices)
    business_name = models.CharField(max_length=36, unique=True, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f'{self.email}'