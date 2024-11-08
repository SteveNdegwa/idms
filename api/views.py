import base64
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.backend.services import APIUserService
from base.models import State
from systems.backend.services import SystemService
from users.backend.decorators import user_login_required
from utils.common import generate_token
from utils.get_request_data import get_request_data
from utils.transaction_log_base import TransactionLogBase

lgr = logging.getLogger(__name__)

class APIManager(TransactionLogBase):
    @staticmethod
    @csrf_exempt
    def generate_token(request):
        """
        Generates an access token for system to system communication
        @params: WSGI Request
        @return: success message and token or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            username = data.get("consumer_key", "")
            password = data.get("consumer_secret", "")
            if not username or not password:
                return JsonResponse({"code": "999.999.001", "message": "Credentials not provided"})
            api_user =  APIUserService().get(username=username)
            if not api_user:
                return JsonResponse({"code": "999.999.002", "message": "Wrong credentials"})
            if not api_user.check_password(password):
                return JsonResponse({"code": "999.999.003", "message": "Wrong credentials"})
            credentials = ''.join(([username, ':', password]))
            credentials_bytes = credentials.encode('utf-8')
            base64_bytes = base64.b64encode(credentials_bytes)
            basic_auth = base64_bytes.decode('utf-8')
            return JsonResponse({"code": "100.000.000", "message": "Token generated successfully", "token": basic_auth})
        except Exception as ex:
            lgr.exception("API Manager - generate_token exception: %s" % ex)
            return JsonResponse({"code": "999.999.999", "message": "Generate token failed with an exception"})


    @staticmethod
    @csrf_exempt
    @user_login_required
    def create_api_user(request):
        """
        Creates an API User
        @params: WSGI Request
        @return: success message and api keys data or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            system = data.get("system", "")
            if not system:
                return JsonResponse({"code": "999.999.001", "message": "System not provided"})
            system = SystemService().get(name=system, state=State.active())
            if not system:
                return JsonResponse({"code": "999.999.002", "message": "System does not exist"})
            if APIUserService().get(system=system):
                return JsonResponse({"code": "999.999.003", "message": "API user already exists"})
            consumer_key = ''.join(["CK_", generate_token(6)])
            consumer_secret = generate_token(9)
            api_user = APIUserService().create(system=system, username=consumer_key)
            if not api_user:
                return JsonResponse({"code": "999.999.004", "message": "API user not created"})
            api_user.set_password(consumer_secret)
            api_user.save()
            return JsonResponse({
                "code": "100.000.000",
                "message": "API user created successfully",
                "data": {
                    "consumer_key": consumer_key,
                    "consumer_secret": consumer_secret
                }
            })
        except Exception as ex:
            lgr.exception("API Manager - create_api_user exception: %s" % ex)
            return JsonResponse({"code": "999.999.999", "message": "Create API user failed with an exception"})

    @staticmethod
    @csrf_exempt
    @user_login_required
    def refresh_api_keys(request):
        """
        Refreshes consumer key and secret
        @params: WSGI Request
        @return: success message and api keys data or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            system = data.get("system", "")
            if not system:
                return JsonResponse({"code": "999.999.001", "message": "System not provided"})
            system = SystemService().get(name=system, state=State.active())
            if not system:
                return JsonResponse({"code": "999.999.002", "message": "System doesCreate API user not exist"})
            api_user = APIUserService().get(system=system)
            if api_user:
                api_user.delete()
            consumer_key = ''.join(["CK_", generate_token(6)])
            consumer_secret = generate_token(9)
            api_user = APIUserService().create(system=system, username=consumer_key)
            if not api_user:
                return JsonResponse({"code": "999.999.004", "message": "API user not created"})
            api_user.set_password(consumer_secret)
            api_user.save()
            return JsonResponse({
                "code": "100.000.000",
                "message": "API keys refreshed successfully",
                "data": {
                    "consumer_key": consumer_key,
                    "consumer_secret": consumer_secret
                }
            })
        except Exception as ex:
            lgr.exception("API Manager - refresh_api_keys exception: %s" % ex)
            return JsonResponse({"code": "999.999.999", "message": "Refresh API keys failed with an exception"})
