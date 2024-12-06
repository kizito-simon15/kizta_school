# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from apps.students.models import Student
from apps.staffs.models import Staff  # Import Staff model

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')  # Add this line
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # Add this line

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

class ParentUser(CustomUser):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True, blank=True, default=None)
    parent_first_name = models.CharField(max_length=200, blank=True, null=True)
    parent_middle_name = models.CharField(max_length=200, blank=True, null=True)
    parent_last_name = models.CharField(max_length=200, blank=True, null=True)

class TeacherUser(CustomUser):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, default=None)

class BursorUser(CustomUser):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, default=None)

class SecretaryUser(CustomUser):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, default=None)

class AcademicUser(CustomUser):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, default=None)