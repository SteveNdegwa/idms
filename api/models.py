from django.contrib.auth.hashers import make_password, check_password
from django.db import models

from api.managers import APIUSerManager
from base.models import BaseModel, State
from systems.models import System


class APIUser(BaseModel):
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    last_activity = models.DateTimeField(null=True, blank=True, editable=False)
    state = models.ForeignKey(State, default=State.active, on_delete=models.CASCADE)

    objects = APIUSerManager()
    SYNC_MODEL = False

    def __str__(self):
        return "%s - %s" % (self.system.name, self.username)

    class Meta(object):
        ordering = ('-date_created',)
        verbose_name = 'API user'
        verbose_name_plural = 'API users'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)
