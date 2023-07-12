from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, backjoon_id, github_id, password=None, **extra_fields):
        if not backjoon_id:
            raise ValueError('The given backjoon_id must be set')
        if not github_id:
            raise ValueError('The given github_id must be set')

        user = self.model(
            backjoon_id=backjoon_id,
            github_id=github_id,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, backjoon_id, github_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(backjoon_id, github_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    backjoon_id = models.CharField(max_length=255, unique=True)
    github_id = models.CharField(max_length=255, unique=True)
    profile_image = models.URLField(blank=True, null=True, default="")
    company = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'backjoon_id'
    REQUIRED_FIELDS = ['github_id']

    def __str__(self):
        return self.backjoon_id
