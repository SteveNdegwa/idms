import logging
import random

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from base.models import State
from organisations.backend.services import OrganisationService
from users.backend.services import UserService, RoleService
from systems.backend.services import SystemService
from utils.get_request_data import get_request_data

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

class UserAdministration(object):
    @csrf_exempt
    def create_user(self, request):
        """
        Creates a person
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            username = data.get("username", "")
            if not username:
                return JsonResponse({"code": "999.999.001", "message": "Username not provided"})
            if UserService().get(username=username, state=State.active_state):
                return JsonResponse({"code": "999.999.002", "message": "Username already exists"})
            organisation = data.get("organisation", "")
            organisation = OrganisationService().filter(Q(name=organisation) | Q(remote_code=organisation))
            organisation = organisation.order_by('-date_created').first() if organisation else None
            role = data.get("role", "")
            role = RoleService().get(name=role ,state=State.active_state)
            if not role:
                return JsonResponse({"code": "999.999.003", "message": "Role provided not valid"})
            k = {
                "username": username,
                "first_name": data.get("first_name" ,""),
                "last_name": data.get("last_name" ,""),
                "other_name": data.get("other_name" ,""),
                "phone_number": data.get("phone_number" ,""),
                "email": data.get("email" ,""),
                "terms_and_conditions_accepted": data.get("terms_and_conditions_accepted" ,False),
                "language_code": data.get("language_code" ,"en"),
                "role": role,
                "organisation": organisation,
            }
            user = UserService().create(**k)
            if not user:
                return JsonResponse({"code": "999.999.004", "message": "User not created"})
            systems = data.get("systems", [])
            if systems:
                user.systems.add([SystemService().get(name=system) for system in systems])
                user.save()
            password = generate_password()
            user.set_password(password)
            #TODO: SEND NOTIFICATION
            return JsonResponse({"code": "100.000.000", "message": "User created successfully"})
        except Exception as e:
            lgr.exception("Create user exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Create user failed with an exception"})

    @csrf_exempt
    def delete_user(self, request):
        """
        Creates a person
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            if not UserService().get(id=user_id, state=State.active_state):
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            if not UserService().update(pk=user_id, state=State.inactive_state):
                return JsonResponse({"code": "999.999.002", "message": "User not deleted"})
            return JsonResponse({"code": "100.000.000", "message": "User deleted successfully"})
        except Exception as e:
            lgr.exception("Delete user exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Delete user failed with an exception"})

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
            if not UserService().get(id=user_id, state=State.active_state):
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            username = data.get("username", "")
            if not username:
                return JsonResponse({"code": "999.999.002", "message": "Username not provided"})
            if UserService().get(~Q(id=user_id), username=username, state=State.active_state):
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
        try:
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active_state)
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            new_password = data.get("password")
            if not new_password:
                return JsonResponse({"code": "999.999.002", "message": "Password not provided"})
            user.set_password(new_password)
            return JsonResponse({"code": "100.000.000", "message": "Password changed successfully"})
        except Exception as e:
            lgr.exception("Update password exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Change password failed with an exception"})

    @csrf_exempt
    def reset_password(self, request):
        """
        Resets a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active_state)
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            password = generate_password()
            user.set_password(password)
            # TODO: SEND NOTIFICATION
            return JsonResponse({"code": "100.000.000", "message": "Password reset successfully"})
        except Exception as e:
            lgr.exception("Update password exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Reset password failed with an exception"})

    @csrf_exempt
    def change_role(self, request):
        """
        Resets a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id" ,"")
            if not UserService().get(id=user_id, state=State.active_state):
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            role = data.get("role", "")
            role = RoleService().get(name=role, state=State.active_state)
            if not role:
                return JsonResponse({"code": "999.999.003", "message": "Role provided not valid"})
            if not UserService().update(pk=user_id, role=role):
                return JsonResponse({"code": "999.999.004", "message": "Role not changed"})
            return JsonResponse({"code": "100.000.000", "message": "Role changed successfully"})
        except Exception as e:
            lgr.exception("Change role exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Change role failed with an exception"})





