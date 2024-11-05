from api.models import APIUser
from utils.servicebase import ServiceBase


class APIUserService(ServiceBase):
    manager = APIUser.objects