import logging
import uuid

from django.db import models

lgr = logging.getLogger(__name__)
lgr.propagate = False

class BaseModel(models.Model):
    id = models.UUIDField(max_length=100, default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta(object):
        abstract = True

class GenericBaseModel(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    class Meta(object):
        abstract = True

class State(GenericBaseModel):
    def __str__(self):
        return self.name

    @classmethod
    def active_state(cls):
        try:
            state = cls.objects.get(name="Active")
            return state
        except Exception as e:
            lgr.exception("State model - active_state exception: %s" % e)
            return None

    @classmethod
    def inactive_state(cls):
        try:
            state = cls.objects.get(name="Inactive")
            return state
        except Exception as e:
            lgr.exception("State model - inactive_state exception: %s" % e)
            return None


class Country(GenericBaseModel):
    code = models.CharField(max_length=10, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active_state, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.name, self.code)

    class Meta:
        ordering = ('-date_created',)

    @classmethod
    def default_country(cls):
        try:
            return Country.objects.get(code="KE")
        except Exception as e:
            lgr.exception("Country model - default_country exception: %s" % e)
            return None



