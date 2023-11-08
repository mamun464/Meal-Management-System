from django.db import models
import os
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager

# Create your CustomUserManager here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, fullName, phone_no,password=None, password2=None,**extra_fields,):

       
        print(f"Input: {email}")
        
        if not phone_no:
            raise ValueError("Phone Number must be provided")
        if not password:
            raise ValueError('Password is not provided')

        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',False)

        user = self.model(
            email=email.lower(),
            fullName = fullName,
            phone_no = phone_no,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        # print(user)
        return user

    def create_superuser(self, email, password, fullName, phone_no, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, password, fullName, phone_no, **extra_fields)
    



# Create your User Model here.
class CustomUser(AbstractBaseUser,PermissionsMixin):
    # Abstractbaseuser has password, last_login, is_active by default
    username = None
    fullName = models.CharField(max_length=100, null=False)
    email = models.EmailField(db_index=True, unique=True,null=False, max_length=254)
    user_profile_img = models.ImageField(upload_to="profile",null=True)
    phone_no=models.CharField(db_index=True,max_length=20, null=False,unique=True)

    is_staff = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_active = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(default=False) # this field we inherit from PermissionsMixin.


    

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_no'
    REQUIRED_FIELDS = ['email','fullName']

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'


    def __str__(self):
            return f"{self.fullName} ({self.phone_no})"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    
    def save(self, *args, **kwargs):
        # Check if an old image exists
        if self.pk:
            old_instance = self.__class__.objects.get(pk=self.pk)
            if old_instance.user_profile_img:
                # Delete the old image file from the filesystem
                if os.path.isfile(old_instance.user_profile_img.path):
                    os.remove(old_instance.user_profile_img.path)
        super().save(*args, **kwargs)
    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_superuser