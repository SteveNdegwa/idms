import logging

from functools import wraps

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from base.models import State
from identities.backend.services import IdentityService
from utils.get_request_data import get_request_data

lgr = logging.getLogger(__name__)


def user_login_required(inner_function):
    @wraps(inner_function)
    def _wrapped_function(*args, **kwargs):
        try:
            for k in args:
                if isinstance(k, WSGIRequest):
                    data = get_request_data(k)
                    token = data.get('token', "")
                    if IdentityService().filter(token=token, state=State.active()):
                        return inner_function(*args, **kwargs)
                    """ Allows customers to create account without being logged in """
                    if inner_function.__name__ == "create_user" and data.get('role', "") == "Customer":
                        return inner_function(*args, **kwargs)
            return JsonResponse({"code": "888.888.001", "message": "Not authenticated"})
        except Exception as e:
            lgr.exception("user_login_required decorator exception - %s" % str(e))
            return JsonResponse({"code": "888.888.888", "message": "Not authenticated"})
    return _wrapped_function
