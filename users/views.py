import logging
import random

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from base.models import State
from organisations.backend.services import OrganisationService
from users.backend.services import UserService, RoleService
from systems.backend.services import SystemService
from utils.common import create_notification_detail
from utils.get_request_data import get_request_data
from utils.transaction_log_base import TransactionLogBase

lgr = logging.getLogger(__name__)
lgr.propagate = False


def generate_password(length=6):
    """
    This function generates the random passwords for users.
    @param length: The number of characters the password should have. Defaults to 6.
    @type length: int
    @return: The generated password.
    @rtype: str
    """
    import string
    groups = [
        string.ascii_uppercase.replace('O', '').replace('I', ''), string.digits,
        string.ascii_lowercase.replace('o', '').replace('i', '').replace('l', ''), '!#%&+:;?@[]_{}']
    cln = [random.choice(groups[n]) for n in range(4)]
    for m in range(length):
        if len(cln) >= length:
            break
        cln.append(random.choice(groups[int(random.choice('0123'))]))
    random.shuffle(cln)
    return ''.join(cln)

class UsersAdministration(TransactionLogBase):
    @csrf_exempt
    def create_user(self, request):
        """
        Creates a person
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("CreateUser", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            username = data.get("username", "")
            if not username:
                response = {"code": "999.999.002", "message": "Username not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            # TODO: ENFORCE EMAIL AND PHONE NUMBER UNIQUENESS FOR SAME SYSTEM
            email = data.get("email", "")
            if not email:
                response = {"code": "999.999.003", "message": "Email not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if UserService().get(username=username, state=State.active()):
                response = {"code": "999.999.004", "message": "Username already exists"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            organisation = data.get("organisation", "")
            organisation = OrganisationService().filter(Q(name=organisation) | Q(remote_code=organisation))
            organisation = organisation.order_by('-date_created').first() if organisation else None
            role = data.get("role", "")
            role = RoleService().get(name=role, state=State.active())
            if not role:
                response = {"code": "999.999.005", "message": "Role provided not valid"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            k = {
                "username": username,
                "email": email,
                "first_name": data.get("first_name" ,""),
                "last_name": data.get("last_name" ,""),
                "other_name": data.get("other_name" ,""),
                "phone_number": data.get("phone_number" ,""),
                "terms_and_conditions_accepted": data.get("terms_and_conditions_accepted" ,False),
                "language_code": data.get("language_code" ,"en"),
                "role": role,
                "organisation": organisation,
            }
            user = UserService().create(**k)
            if not user:
                response = {"code": "999.999.006", "message": "User not created"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            systems = data.get("systems", [])
            for system in systems:
                system = str(system).upper().strip()
                user.systems.add(SystemService().get(name=system))
            user.save()
            password = generate_password()
            user.set_password(password)
            notification_msg = "Welcome, use your phone number or email to login and %s as your password" % password
            notification_details = create_notification_detail(
                message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
            response = {"code": "100.000.000", "message": "User created successfully"}
            self.complete_transaction(transaction, response=response, notification_details=notification_details)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Create user exception: %s" % e)
            response = {"code": "999.999.999", "message": "Create user failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    def delete_user(self, request):
        """
        Creates a person
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("DeleteUser", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                response = {"code": "999.999.002", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if not UserService().update(pk=user_id, state=State.inactive()):
                response = {"code": "999.999.003", "message": "User not deleted"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            notification_msg = "Your account has been deleted successfully"
            notification_details = create_notification_detail(
                message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
            response = {"code": "100.000.000", "message": "User deleted successfully"}
            self.complete_transaction(transaction, response=response, notification_details=notification_details)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Delete user exception: %s" % e)
            response = {"code": "999.999.999", "message": "Delete user failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    def update_personal_details(self, request):
        """
        Edits a person's details
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            if not UserService().get(id=user_id, state=State.active()):
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            username = data.get("username", "")
            if not username:
                return JsonResponse({"code": "999.999.002", "message": "Username not provided"})
            if UserService().get(~Q(id=user_id), username=username, state=State.active()):
                return JsonResponse({"code": "999.999.003", "message": "Username already exists"})
            k = {
                "username": username,
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "other_name": data.get("other_name", ""),
                "phone_number": data.get("phone_number", ""),
                "email": data.get("email", ""),
            }
            user = UserService().update(pk=user_id, **k)
            if not user:
                return JsonResponse({"code": "999.999.005", "message": "User not updated"})
            return JsonResponse({"code": "100.000.000", "message": "User updated successfully"})
        except Exception as e:
            lgr.exception("Update personal details exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Update personal details failed with an exception"})

    @csrf_exempt
    def change_password(self, request):
        """
        Changes a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("ChangePassword", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                response = {"code": "999.999.001", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            new_password = data.get("password")
            if not new_password:
                response = {"code": "999.999.002", "message": "Password not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            user.set_password(new_password)
            response = {"code": "100.000.000", "message": "Password changed successfully"}
            self.complete_transaction(transaction, response=response)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Update password exception: %s" % e)
            response = {"code": "999.999.999", "message": "Change password failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    def reset_password(self, request):
        """
        Resets a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("ResetPassword", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                response = {"code": "999.999.002", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            password = generate_password()
            user.set_password(password)
            notification_msg = "Your password was reset. Please use %s as your password" % password
            notification_details = create_notification_detail(
                message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
            response = {"code": "100.000.000", "message": "Password reset successfully"}
            self.complete_transaction(transaction, response=response, notification_details=notification_details)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Update password exception: %s" % e)
            response = {"code": "999.999.999", "message": "Reset password failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    def change_role(self, request):
        """
        Resets a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("ChangePassword", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            user_id = data.get("user_id" ,"")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                response = {"code": "999.999.002", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            role = data.get("role", "")
            role = RoleService().get(name=role, state=State.active())
            if not role:
                response = {"code": "999.999.003", "message": "Role provided not valid"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if not UserService().update(pk=user_id, role=role):
                response = {"code": "999.999.004", "message": "Role not changed"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            notification_msg = "Your role was changed to %s successfully" % role.name
            notification_details = create_notification_detail(
                message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
            response = {"code": "100.000.000", "message": "Role changed successfully"}
            self.complete_transaction(transaction, response=response, notification_details=notification_details)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Change role exception: %s" % e)
            response = {"code": "999.999.999", "message": "Change role failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)
