from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password


class APIUSerManager(BaseUserManager):
    def _create_user(self, system, username, password, **extra_fields):
        if not system:
            raise ValueError("System instance must be provided")
        if not username:
            raise ValueError("Username must be provided")
        if not password:
            raise ValueError("Password must be provided")
        user = self.model(system=system, username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, system=None, username=None, password=None, **extra_fields):
        return self._create_user(system, username, password, **extra_fields)

    def create(self, system=None, username=None, password=None, **extra_fields):
        return self._create_user(system, username, password, **extra_fields)

