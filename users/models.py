import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

from base.models import BaseModel, State, GenericBaseModel
from organisations.models import Organisation
from systems.models import System
from users.managers import UserManager

lgr = logging.getLogger(__name__)
lgr.propagate = False


class Role(GenericBaseModel):
    state = models.ForeignKey(State, default=State.active_state, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-date_created',)

class Permission(GenericBaseModel):
    state = models.ForeignKey(State, default=State.active_state, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-date_created',)

class RolePermission(BaseModel):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, default=State.active_state, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.role.name, self.permission.name)

    class Meta:
        ordering = ('-date_created',)
        unique_together = ('role', 'permission')


class User(BaseModel, AbstractUser):
    other_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    terms_and_conditions_accepted = models.BooleanField(default=False)
    language_code = models.CharField(max_length=5, default='en')
    last_activity = models.DateTimeField(null=True, blank=True, editable=False)
    systems = models.ManyToManyField(System)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active_state, on_delete=models.CASCADE)

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('-date_created',)

    def set_password(self, raw_password):
        try:
            self.password = make_password(raw_password)
            self.save()
            return True
        except Exception as e:
            lgr.exception("User model - set password exception: %s" % e)
            return False

    def full_name(self):
        return "%s %s %s" % (self.first_name, self.other_name, self.last_name)

