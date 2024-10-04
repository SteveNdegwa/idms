from django.db import models

from base.models import GenericBaseModel


class System(GenericBaseModel):
    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-date_created',)