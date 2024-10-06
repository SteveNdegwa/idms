from base.models import State, Country
from utils.servicebase import ServiceBase


class StateService(ServiceBase):
    manager = State.objects

class CountryService(ServiceBase):
    manager = Country.objects