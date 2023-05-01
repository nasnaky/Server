from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.datetime_safe import datetime
from taggit.managers import TaggableManager


class UserManager(BaseUserManager):
    def create_user(self, phone, email, password, **kwargs):
        if not phone:
            raise ValueError('Users must have an phone')
        user = self.model(
            email=email,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        superuser = self.create_user(
            email=email,
            phone=phone,
            password=password,
        )

        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True

        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    phoneNumberRegex = RegexValidator(regex=r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$')
    phone = models.CharField(validators=[phoneNumberRegex], max_length=11, unique=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    def __int__(self):
        return self.id


class PRODUCT(models.Model):
    tags = TaggableManager()
    money = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    name = models.TextField(default="user")
    content = models.TextField(default="content")
    barcode = models.ImageField(upload_to='images/', null=False, blank=False)
    max_data = models.DateField()
    size = models.BooleanField(default=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
