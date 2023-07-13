from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, kakao_id, password=None, backjoon_id=None, github_id=None, **extra_fields):
        if not kakao_id:
            raise ValueError('The given kakao_id must be set')

        user = self.model(
            kakao_id=kakao_id,
            backjoon_id=backjoon_id,
            github_id=github_id,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, kakao_id, backjoon_id=None, github_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(kakao_id, backjoon_id, github_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    kakao_id = models.CharField(max_length=255, unique=True)
    backjoon_id = models.CharField(max_length=255, null=True, blank=True)
    github_id = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default="")
    company = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'kakao_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.kakao_id
