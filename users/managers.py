from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """

    use_in_migrations = True

    def create_user(self, email, phone, password=None, **extra_fields):
        """
        Creates and saves a new user with the given email and password.

        :param email: Email address of the user.
        :param password: Password for the user.
        :param extra_fields: Extra fields for the user model.
        :return: Newly created user object.
        :raises ValueError: If email is not provided.
        """
        if not email:
            raise ValueError('Email address must be provided')
        if not phone:
            raise ValueError('Phone number must be provided')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        if password:
            user.set_password(password)  #hash the password
        user.save(using=self._db)
        return user


    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'Admin')

        return self.create_user(email, phone, password, **extra_fields)
