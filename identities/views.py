import calendar
import logging

from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from base.models import State
from identities.backend.services import IdentityService
from users.backend.services import UserService
from utils.common import create_notification_detail
from utils.generate_system_aoth_otp import OAuthHelper
from utils.get_request_data import get_request_data
from utils.transaction_log_base import TransactionLogBase

lgr = logging.getLogger(__name__)
lgr.propagate = False


class IdentitiesAdministration(TransactionLogBase):
    @csrf_exempt
    def login(self, request):
        """
        Logs in a user - Either through username or email or phone number
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            credential = data.get("credential", "")
            password = data.get("password", "")
            system = data.get("system", "")
            source_ip = data.get("source_ip", "")
            if not credential or not password:
                return JsonResponse({"code": "999.999.001", "message": "Login credentials not provided"})
            if not system:
                return JsonResponse({"code": "999.999.002", "message": "System not provided"})
            user = UserService().filter(
                Q(username=credential) | Q(email=credential) | Q(phone_number=credential), systems__name=system,
                state=State.active())
            if not user:
                return JsonResponse({"code": "999.999.003", "message": "User not found"})
            user = user.first()
            if not user.check_password(password):
                return JsonResponse({"code": "999.999.004", "message": "Wrong credentials"})
            IdentityService().filter(
                user=user, state=State.active()).exclude(date_created__date=timezone.now()).update(state=State.expired())
            oauth = IdentityService().filter(
                Q(state=State.active()) | Q(state=State.activation_pending()), user=user,
                date_created__date=timezone.now())
            oauth = oauth.order_by('-date_created').first() if oauth else None
            if not oauth:
                oauth = IdentityService().filter(user=user, date_created__date=timezone.now(), state=State.expired())
                oauth = oauth.order_by('-date_created').first() if oauth else None
                oauth = IdentityService().update(pk=oauth.id, state=State.activation_pending()) if oauth else None
                if not oauth:
                    generated = OAuthHelper.generate_device_otp()
                    otp = list(generated)
                    key = (otp[1]).decode()
                    totp =  otp[0]
                    oauth = IdentityService().create(
                        user=user, source_ip=source_ip, totp_key=key, totp_time_value=otp[2],
                        state=State.activation_pending())
                    if not oauth:
                        return JsonResponse({"code": "999.999.005", "message": "Identity not created"})
                    notification_msg = "Welcome. Your OTP is %s" % totp.decode()
                    notification_details = create_notification_detail(
                        message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
                    self.send_notification(notifications=notification_details)
            oauth = oauth.extend()
            user.update_last_activity()
            return JsonResponse({
                "code": "100.000.000",
                "message": "Login successful",
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
                ~Q(user=None), state__in=[State.active(), State.activation_pending(), State.expired()], token=token,
                expires_at__gt=timezone.now())
            oauth = oauth.order_by('-date_created').first() if oauth else None
            if not oauth:
                return JsonResponse({"code": "999.999.001", "message": "Identity not found"})
            generated = OAuthHelper.verify_device(oauth.totp_key, str(totp).strip(), float(oauth.totp_time_value))
            if not generated:
                return JsonResponse({"code": "999.999.002", "message": "Invalid OTP"})
            oauth = IdentityService().update(pk=oauth.id, state=State.active())
            if not oauth:
                return JsonResponse({"code": "999.999.003", "message": "Identity not activated"})
            oauth = oauth.extend()
            return JsonResponse({
                "code": "100.000.000",
                "message": "OTP verified",
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
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            IdentityService().filter(user=user, state=State.active()).update(state=State.expired())
            return JsonResponse({"code": "100.000.000", "message": "User logged out successfully"})
        except Exception as e:
            lgr.exception("Logout exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Logout failed with an exception"})

    @csrf_exempt
    def check_login_status(self, request):
        """
        Checks if a user is logged in
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            token = data.get("token", "")
            oauth = IdentityService().filter(
                ~Q(user=None), state=State.active(), token=token, expires_at__gt=timezone.now())
            if not oauth:
                return JsonResponse({"code": "999.999.001", "message": "User not logged in"})
            return JsonResponse({"code": "100.000.000", "message": "User is logged in"})
        except Exception as e:
            lgr.exception("Check login status exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Check login status failed with an exception"})


