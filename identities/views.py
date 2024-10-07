import calendar
import logging

from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from base.models import State
from identities.backend.services import IdentityService
from users.backend.services import UserService
from utils.generate_system_aoth_otp import OAuthHelper
from utils.get_request_data import get_request_data

lgr = logging.getLogger(__name__)
lgr.propagate = False

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class IdentitiesAdministration(object):
    @csrf_exempt
    def login(self, request):
        """
        Logs in a user
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            username = data.get("username", "")
            password = data.get("password", "")
            if not username:
                return JsonResponse({"code": "999.999.001", "message": "Username not provided"})
            user = UserService().get(username=username, state=State.active)
            if not user:
                return JsonResponse({"code": "999.999.002", "message": "User not found"})
            if not user.check_password(password):
                return JsonResponse({"code": "999.999.003", "message": "Wrong credentials"})
            oauth = IdentityService().filter(username=username, state=State.active)
            oauth = oauth.order_by('-date_created').first() if oauth else None
            if not oauth:
                oauth = IdentityService().filter(user=user, date_created__date=timezone.now(), state=State.expired)
                oauth = oauth.order_by('-date_created').first() if oauth else None
                oauth = IdentityService().update(pk=oauth.id, state=State.activation_pending) if oauth else None
                if not oauth:
                    generated = OAuthHelper.generate_device_otp()
                    otp = list(generated)
                    key = (otp[1]).decode()
                    oauth = IdentityService().create(
                        user=user, source_ip=get_client_ip(request), totp_key=key, totp_time_value=otp[2],
                        state=State.activation_pending)
                    if not oauth:
                        return JsonResponse({"code": "999.999.004", "message": "Identity not created"})
                    # TODO: SEND NOTIFICATION
            oauth = oauth.extend()
            user.update_last_activity()
            return JsonResponse({
                "code": "100.000.000",
                "data": {
                    "token": str(oauth.token),
                    "user_id": str(user.id),
                    "expires_at": calendar.timegm(oauth.expires_at.timetuple())
                }
            })
        except Exception as e:
            lgr.exception("Login exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Login failed with an exception"})

    @csrf_exempt
    def verify_totp(self, request):
        """
        Verifies the TOTP of a user
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            token = data.get("token", "")
            totp = data.get("otp", "")
            oauth = IdentityService().filter(
                ~Q(user=None), state__in=[State.active, State.activation_pending, State.expired], token=token,
                expires_at__gt=timezone.now())
            oauth = oauth.order_by('-date_created').first() if oauth else None
            if not oauth:
                return JsonResponse({"code": "999.999.001", "message": "Identity not found"})
            generated = OAuthHelper.verify_device(oauth.totp_key, str(totp).strip(), float(oauth.totp_time_value))
            if not generated:
                return JsonResponse({"code": "999.999.002", "message": "Invalid OTP"})
            oauth = IdentityService().update(pk=oauth.id, state=State.active)
            if not oauth:
                return JsonResponse({"code": "999.999.003", "message": "Identity not activated"})
            oauth = oauth.extend()
            return JsonResponse({
                "code": "100.000.000",
                "data": {
                    "activated": True,
                    "expires_at": calendar.timegm(oauth.expires_at.timetuple())
                }
            })
        except Exception as e:
            lgr.exception("Verify totp exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Verify totp failed with an exception"})

    @csrf_exempt
    def logout(self, request):
        """
        Logs out out a user
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id" , "")
            user = UserService().get(id=user_id, state=State.active)
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            oauth = IdentityService().filter(user=user, state=State.active)
            if oauth:
                oauth.update(state=State.expired)
            return JsonResponse({"code": "100.000.000", "message": "User logged out successfully"})
        except Exception as e:
            lgr.exception("Logout exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Logout failed with an exception"})

