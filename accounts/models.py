from __future__ import unicode_literals
from django.db import models
from django.db.transaction import atomic
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
import uuid


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        try:
            with atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except Exception as e:
            raise e

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    User_type = (
        ('1', 'Normal User'),
        ('2', 'Shop User'),
        ('3', 'Admin')
    )
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    email = models.EmailField(max_length=40, unique=True)
    name = models.CharField(max_length=30, blank=True)
    profile = models.ImageField(upload_to='media/user/profile/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=250, null=True)
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    user_type = models.CharField(max_length=250, choices=User_type)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "User"

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    def __str__(self):
        return self.name