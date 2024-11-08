import logging

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from base.models import BaseModel, State, GenericBaseModel, Country
from organisations.models import Organisation
from systems.models import System

lgr = logging.getLogger(__name__)
lgr.propagate = False


class Role(GenericBaseModel):
    state = models.ForeignKey(State, default=State.active, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-date_created',)

class Permission(GenericBaseModel):
    state = models.ForeignKey(State, default=State.active, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-date_created',)

class RolePermission(BaseModel):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, default=State.active, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.role.name, self.permission.name)

    class Meta:
        ordering = ('-date_created',)
        unique_together = ('role', 'permission')


class Profile(GenericBaseModel):
    EmploymentType = [
        ('Self Employed', 'Self Employed'),
        ('Employed', 'Employed'),
        ('Unemployed', 'Unemployed'),
        ('Freelance', 'Freelance'),
        ('Student', 'Student'),
    ]

    DEFAULT_EMPLOYMENT = "Other"
    id_no = models.CharField(max_length=100, null=True, blank=True)
    other_phone_number = models.CharField(max_length=20, blank=True, null=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    employment_type = models.CharField(
        max_length=100, default=DEFAULT_EMPLOYMENT, blank=False, null=False, choices=EmploymentType)
    income_from_investments = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=100, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    work_place_grants_or_allowance = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    country_of_work = models.ForeignKey(Country, default=Country.default_country, on_delete=models.CASCADE)
    physical_work_address = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(
        Country, default=Country.default_country, related_name='profile_country', on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.id_no, self.country_of_work)

    class Meta(object):
        ordering = ('-date_created',)


class User(BaseModel, AbstractUser):
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    DEFAULT_GENDER = "Other"

    other_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=100, default=DEFAULT_GENDER, choices=GENDER)
    terms_and_conditions_accepted = models.BooleanField(default=False)
    language_code = models.CharField(max_length=5, default='en')
    last_activity = models.DateTimeField(null=True, blank=True, editable=False)
    systems = models.ManyToManyField(System)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, default=State.active, on_delete=models.CASCADE)

    objects = UserManager()
    SYNC_MODEL = False

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('-date_created',)

    def update_last_activity(self):
        """
        Update the last time the user was activity
        """
        self.last_activity = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save method to make sure user is saved with a role
        """
        if not self.is_superuser and not self.role:
            raise ValidationError("A user must have a role")
        super(User, self).save(*args, **kwargs)

    def full_name(self):
        return "%s %s %s" % (self.first_name, self.other_name, self.last_name)

    @property
    def get_permissions(self):
        """
        Gets all user permissions based on their role
        """
        permissions = []
        try:
            role_permissions = list(RolePermission.objects.filter(role=self.role))
            for role_permission in role_permissions:
                permissions.append(role_permission.permission.name)
            return permissions
        except Exception as e:
            lgr.exception("User model - get permissions exception: %s" % e)
            return permissions


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """ Creates a profile after a user is created """
    if created and not instance.is_superuser and  instance.role.name in ["Customer"] and not instance.profile:
        profile = Profile.objects.create()
        instance.profile = profile
        instance.save()
