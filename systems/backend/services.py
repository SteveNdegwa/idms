from systems.models import System
from utils.servicebase import ServiceBase


class SystemService(ServiceBase):
    manager = System.objects