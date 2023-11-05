from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager

# Create your CustomUserManager here.
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, fullName, phone_no, **extra_fields):
        if not phone_no:
            raise ValueError("Phone Number must be provided")
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            email = self.normalize_email(email),
            fullName = fullName,
            phone_no = phone_no,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, fullName, phone_no, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email, password, fullName, phone_no, password, **extra_fields)

    def create_superuser(self, email, password, fullName, phone_no, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, password, fullName, phone_no, **extra_fields)

# Create your User Model here.
class CustomUser(AbstractBaseUser,PermissionsMixin):
    # Abstractbaseuser has password, last_login, is_active by default

    # email = models.EmailField(db_index=True, unique=True, max_length=254)
    # first_name = models.CharField(max_length=240)
    # last_name = models.CharField(max_length=255)
    # mobile = models.CharField(max_length=50)
    # address = models.CharField( max_length=250)
    username = None
    fullName = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=False,unique=True)
    user_profile_img = models.ImageField(upload_to="profile",null=True)
    phone_no=models.CharField(max_length=20, null=False,unique=True)

    is_staff = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_active = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(default=False) # this field we inherit from PermissionsMixin.

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_no'
    REQUIRED_FIELDS = ['email','fullName']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


    def __str__(self):
            return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_superuser