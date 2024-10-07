from users.models import User, Role, Permission, RolePermission
from utils.servicebase import ServiceBase


class UserService(ServiceBase):
    manager = User.objects

class RoleService(ServiceBase):
    manager = Role.objects

class PermissionService(ServiceBase):
    manager = Permission.objects

class RolePermissionService(ServiceBase):
    manager = RolePermission.objects

