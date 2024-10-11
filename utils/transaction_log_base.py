import json
import logging
import time
from threading import Thread

import requests
from django.conf import settings

from base.backend.services import TransactionService, TransactionTypeService, NotificationTypeService, \
    NotificationService
from base.models import State
from utils.common import json_super_serializer
from utils.get_request_data import get_request_data

lgr = logging.getLogger(__name__)


class TransactionLogBase(object):
    @staticmethod
    def replace_tags(template_string, **kwargs):
        """
        Replaces all the occurrences of replace tags with the passed in arguments.
        @param template_string: The template string we are supposed to replace tags.
        @type template_string: str
        @param kwargs: The key->word arguments representing the tags in the string without []
        @return: The template string replaced accordingly.
        @rtype: str
        """
        try:
            for k, v in kwargs.items():
                template_string = template_string.replace('[%s]' % str(k), str(v))
            return template_string
        except Exception as e:
            lgr.exception('TransactionLogBase replace_tags Exception: %s', e)
        return template_string

    @staticmethod
    def log_transaction(transaction_type, **kwargs):
        """
        Logs a transaction of the given type having the provided arguments.
        If transaction reference is not passed, it's generated. Same case for state, defaults to Active.
        @param transaction_type: The name of the type of transaction we are creating.
        @type transaction_type: str
        @param kwargs: Key word arguments to generate the transaction with.
        @return: The created transaction.
        @rtype: Transaction | None
        """
        try:
            transaction_type = TransactionTypeService().get(name=transaction_type)
            if not transaction_type:
                return None
            kwargs.setdefault("state", State.active())
            request = kwargs.setdefault("request", {})
            if request:
                # kwargs.setdefault("user", getattr(request, "user", None))
                data = get_request_data(request)
                kwargs.setdefault("source_ip", data.get("source_ip", ""))
                kwargs["request"] = data
            return TransactionService().create(transaction_type=transaction_type, **kwargs)
        except Exception as e:
            lgr.exception('TransactionLogBase log_transaction Exception: %s', e)
        return None

    def complete_transaction(self, transaction_obj, **kwargs):
        """
        Marks the transaction object as complete.
        @param transaction_obj: The transaction we are updating.
        @type transaction_obj: Transaction
        @param kwargs: Any key->word arguments to pass to the method.
        @return: The transaction updated.
        @rtype: Transaction | None
        """
        try:
            kwargs.setdefault("state", State.completed())
            notifications = kwargs.setdefault("notification_details", [])
            Thread(target=self.send_notification, args=(notifications, transaction_obj)).start()
            return TransactionService().update(pk=transaction_obj.id, **kwargs)
        except Exception as e:
            lgr.exception('TransactionLogBase complete_transaction Exception: %s', e)
        return None

    def mark_transaction_failed(self, transaction_obj, **kwargs):
        """
        Marks the transaction object as Failed.
        @param transaction_obj: The transaction we are updating.
        @type transaction_obj: Transaction
        @param kwargs: Any key->word arguments to pass to the method.
        @return: The transaction updated.
        @rtype: Transaction | None
        """
        try:
            kwargs.setdefault("state", State.failed())
            notifications = kwargs.get('notification_details', [])
            Thread(target=self.send_notification, args=(notifications, transaction_obj)).start()
            return TransactionService().update(pk=transaction_obj.id, **kwargs)
        except Exception as e:
            lgr.exception('TransactionLogBase mark_transaction_failed Exception: %s', e)
        return None

    @staticmethod
    def send_notification(notifications, trans=None):
        """
        Sends notifications through the Notifications Bus. The notifications are passed in as a list of dictionaries
        which it then evaluates and makes the http calls
        @param notifications: list of dictionaries for notifications to be sent
        @type notifications: list
        @param trans: The transaction that the notifications are sent against
        @type trans: Transaction Model object
        @return: None
        @rtype: None
        """
        try:
            if not notifications:
                return None
            if not settings.SEND_NOTIFICATIONS:
                return 'success'
            access_token_data = {
                'username': settings.BUS_USERNAME,
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET
            }
            for notification in notifications:
                if notification['message_type'] == '1':
                    notification_name = 'SMS'
                elif notification['message_type'] == '2':
                    notification_name = 'EMAIL'
                else:
                    notification_name = 'SYS'
                notification_type = NotificationTypeService().get(name=notification_name)
                message = json.dumps(notification.get('replace_tags', ''), default=json_super_serializer)
                files = notification.get('files', None)
                destination = notification.get('destination', '')
                noti = NotificationService().create(
                    notification_type=notification_type, title=notification.get('message_code', ''), message=message,
                    destination=destination, state=State.sent())
                if not noti:
                    return 'Notifications Down'
                if notification_name != 'SYS':
                    resp = json.loads(
                        requests.post(
                            url='%s/api/%s/' % (settings.BUS_URL, 'get_access_token'),
                            data=access_token_data, verify=False, timeout=None).text)
                    access_token = resp.get('data', {}).get('token', None)
                    if access_token is None:
                        time.sleep(20)
                        resp = json.loads(
                            requests.post(
                                url='%s/api/%s/' % (settings.BUS_URL, 'get_access_token'),
                                data=access_token_data, verify=False, timeout=None).text)
                        access_token = resp.get('data', {}).get('token', '')
                    if access_token is None:
                        continue
                    notification['token'] = access_token
                    notification['client_id'] = settings.CLIENT_ID
                    notification['app_code'] = settings.APP_CODE
                    notification['replace_tags'] = json.dumps(
                        notification['replace_tags'], default=json_super_serializer)
                    if files:
                        notification_response = json.loads(
                            requests.post(
                                url='%s/api/%s/' % (settings.BUS_URL, 'send_message'), data=notification,
                                verify=False, files=files, timeout=None).text)
                    else:
                        notification_response = json.loads(requests.post(
                            url='%s/api/%s/' % (settings.BUS_URL, 'send_message'), data=notification,
                            verify=False, timeout=None).text)
                    notification_response = notification_response.get('data', {}).get('confirmation_code', None)
                    if notification_response is None:
                        continue
                    if trans is not None:
                        notification_responses = getattr(trans, 'notification_response', None)
                        if notification_responses is not None:
                            notification_responses = notification_responses + "|%s" % notification_response
                        else:
                            notification_responses = notification_response
                        TransactionService().update(trans.id,  notification_response=notification_responses)
                else:
                    if trans is not None:
                        notification_responses = 'Sent'
                        TransactionService().update(trans.id, notification_response=notification_responses)
            return 'success'
        except Exception as e:
            lgr.exception("TransactionLogBase send_notification: %s", e)
        return None