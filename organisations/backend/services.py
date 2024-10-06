from organisations.models import Organisation
from utils.servicebase import ServiceBase


class OrganisationService(ServiceBase):
    manager = Organisation.objects