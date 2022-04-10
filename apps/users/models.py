from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Empty class to override the default user model."""
