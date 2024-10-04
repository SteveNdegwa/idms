import logging

from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import Q

from base.models import BaseModel, State, GenericBaseModel
from organisations.models import Organisation
from systems.models import System

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


class Person(BaseModel):
    username = models.CharField(max_length=100, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    other_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254)
    terms_and_conditions_accepted = models.BooleanField(default=False)
    language_code = models.CharField(max_length=5, default='en')
    last_activity = models.DateTimeField(null=True, blank=True, editable=False)
    systems = models.ManyToManyField(System)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE)
    is_superuser =  models.BooleanField(default=False)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active_state, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        ordering = ('-date_created',)

    def password(self) -> object:
        """ Returns the password instance of a pers on """
        try:
            return Password.objects.filter(person=self, state=State.active_state).order_by('-date_created').first()
        except Exception as e:
            lgr.exception("Person model - get password exception: %s" % e)
        return None

    def set_password(self, raw_password: str) -> bool:
        """ Sets the password for a person """
        try:
            self.save()
            new_pass = Password.objects.create(
                person=self, password=make_password(raw_password), state=State.active_state)
            if new_pass is not None:
                Password.objects.filter(
                    ~Q(pk=new_pass.pk), person=self, state=State.active_state).update(state=State.inactive_state)
            return True
        except Exception as e:
            print('Person model - set password exception: %s' % e)
            return False


class Password(BaseModel):
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE)
    password = models.CharField(max_length=254)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active_state, on_delete=models.CASCADE)
