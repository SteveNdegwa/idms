from identities.models import Identity
from utils.servicebase import ServiceBase


class IdentityService(ServiceBase):
    manager = Identity.objects