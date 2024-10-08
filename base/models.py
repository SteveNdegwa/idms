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
    def active(cls):
        try:
            state = cls.objects.get(name="Active")
            return state
        except Exception as e:
            lgr.exception("State model - active exception: %s" % e)
            return None

    @classmethod
    def inactive(cls):
        try:
            state = cls.objects.get(name="Inactive")
            return state
        except Exception as e:
            lgr.exception("State model - inactive exception: %s" % e)
            return None

    @classmethod
    def expired(cls):
        try:
            state = cls.objects.get(name="Expired")
            return state
        except Exception as e:
            lgr.exception("State model - expired exception: %s" % e)
            return None

    @classmethod
    def activation_pending(cls):
        try:
            state = cls.objects.get(name="Activation Pending")
            return state
        except Exception as e:
            lgr.exception("State model - activation_pending exception: %s" % e)
            return None

    @classmethod
    def completed(cls):
        try:
            state = cls.objects.get(name="Completed")
            return state
        except Exception as e:
            lgr.exception("State model - completed exception: %s" % e)
            return None

    @classmethod
    def failed(cls):
        try:
            state = cls.objects.get(name="Failed")
            return state
        except Exception as e:
            lgr.exception("State model - failed exception: %s" % e)
            return None

    @classmethod
    def sent(cls):
        try:
            state = cls.objects.get(name="Sent")
            return state
        except Exception as e:
            lgr.exception("State model - sent exception: %s" % e)
            return None

class Country(GenericBaseModel):
    code = models.CharField(max_length=10, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active(), on_delete=models.CASCADE)

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

class TransactionType(GenericBaseModel):
    state = models.ForeignKey(State, null=True, blank=True, default=State.active(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Transaction(BaseModel):
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, null=True, blank=True)
    source_ip = models.CharField(max_length=30, null=True, blank=True)
    request = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    notification_response = models.TextField(null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active(), on_delete=models.CASCADE)

    SYNC_MODEL = False

    def __str__(self):
        return self.transaction_type.name

    class Meta:
        ordering = ('-date_created',)

class NotificationType(GenericBaseModel):
    state = models.ForeignKey(State, null=True, blank=True, default=State.active(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Notification(BaseModel):
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    message = models.TextField(max_length=500)
    destination = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    SYNC_MODEL = False

    def __str__(self):
        return '%s - %s' % (self.notification_type, self.destination)

    class Meta:
        ordering = ('-date_created',)



