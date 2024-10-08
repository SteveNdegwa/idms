import logging
from threading import Thread

from base.models import State

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
            t.start()
            return TransactionService().update(transaction_obj.id, **kwargs)
        except Exception as e:
            lgr.exception('complete_transaction Exception: %s', e)
        return None