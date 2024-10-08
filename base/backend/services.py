from base.models import State, Country, TransactionType, Transaction, Notification, NotificationType
from utils.servicebase import ServiceBase


class StateService(ServiceBase):
    manager = State.objects

class CountryService(ServiceBase):
    manager = Country.objects

class TransactionTypeService(ServiceBase):
    manager = TransactionType.objects

class TransactionService(ServiceBase):
    manager = Transaction.objects

class NotificationTypeService(ServiceBase):
    manager = NotificationType.objects

class NotificationService(ServiceBase):
    manager = Notification.objects