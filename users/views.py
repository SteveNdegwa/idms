import logging

from django.db import transaction as trx
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from base.backend.services import CountryService
from base.models import State
from organisations.backend.services import OrganisationService
from organisations.models import Organisation
from users.backend.decorators import user_login_required
from users.backend.services import UserService, RoleService, ProfileService
from systems.backend.services import SystemService
from utils.common import create_notification_detail, generate_password
from utils.get_request_data import get_request_data
from utils.transaction_log_base import TransactionLogBase

lgr = logging.getLogger(__name__)
lgr.propagate = False


class UsersAdministration(TransactionLogBase):
    @csrf_exempt
    @user_login_required
    @trx.atomic
    def create_user(self, request):
        """
        Creates a user
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
            email = data.get("email", "")
            phone_number = data.get("phone_number", "")
            systems = data.pop("systems", [])
            data.pop("source_ip" ,"")
            if not username or not email or not phone_number:
                response = {"code": "999.999.002", "message": "Provide all required details"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if UserService().get(username=username, state=State.active()):
                response = {"code": "999.999.003", "message": "Username already exists"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if UserService().get(email=email, systems__name__in=systems, state=State.active()):
                response = {"code": "999.999.004", "message": "Email address already exists"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if UserService().get(phone_number=phone_number, systems__name__in=systems, state=State.active()):
                response = {"code": "999.999.005", "message": "Phone number already exists"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            role = data.get("role", "")
            role = RoleService().get(name=role, state=State.active())
            if not role:
                response = {"code": "999.999.006", "message": "Role provided not valid"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            data["role"] = role
            if "organisation" in data:
                organisation = data.get("organisation")
                organisation = OrganisationService().filter(Q(name=organisation) | Q(remote_code=organisation))
                if not organisation:
                    response = {"code": "999.999.007", "message": "Invalid organisation"}
                    self.mark_transaction_failed(transaction, response=response)
                    return JsonResponse(response)
                data["organisation"] = organisation
            user = UserService().create(**data)
            if not user:
                raise Exception("User not created - data: %s" % data)
            for system in systems:
                s = SystemService().get(name=system)
                if not s:
                    raise Exception("Invalid system - %s" % system)
                user.systems.add(s)
            password = generate_password()
            user.set_password(password)
            user.save()
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
    @user_login_required
    def delete_user(self, request):
        """
        Deletes a user
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
                raise Exception("User not deleted - user_id: %s" % user_id)
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
    @user_login_required
    def update_personal_details(self, request):
        """
        Edits a user's details
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.pop("user_id", "")
            data.pop("source_ip", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            username = data.get("username", "")
            email = data.get("email", "")
            phone_number = data.get("phone_number", "")
            if (("username" in data and not username) or ("email" in data and not email) or
                    ("phone_number" in data and not phone_number)):
                return JsonResponse({"code": "999.999.002", "message": "Provide all required details"})
            if username and UserService().filter(~Q(id=user_id), username=username, state=State.active()):
                return JsonResponse({"code": "999.999.003", "message": "Username already exists"})
            if email and UserService().filter(
                    ~Q(id=user_id), systems_in=list(user.systems.all()), email=email, state=State.active()):
                return JsonResponse({"code": "999.999.004", "message": "Email already exists"})
            if phone_number and UserService().filter(
                    ~Q(id=user_id), systems_in=list(user.systems.all()), phone_number=phone_number,
                    state=State.active()):
                return JsonResponse({"code": "999.999.005", "message": "Phone number already exists"})
            if "role" in data:
                raise Exception("Role can not be updated")
            if "organisation" in data:
                raise Exception("Organisation can not be updated")
            user = UserService().update(pk=user_id, **data)
            if not user:
                raise Exception("User's personal details not updated' - data: %s" % data)
            return JsonResponse({"code": "100.000.000", "message": "User updated successfully"})
        except Exception as e:
            lgr.exception("Update personal details exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Update personal details failed with an exception"})

    @csrf_exempt
    @user_login_required
    def update_profile(self, request):
        """
       Updates a user's profile
       @params: WSGI Request
       @return: success or failure message
       @rtype: JsonResponse
       """
        try:
            data = get_request_data(request)
            user_id = data.pop("user_id", "")
            data.pop("source_ip", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            if not user.profile:
                return JsonResponse({"code": "999.999.002", "message": "User profile not found"})
            if "country" in data:
                country = data.get("country")
                country = CountryService().filter(Q(name=country) | Q(code=country))
                if not country:
                    return JsonResponse({"code": "999.999.003", "message": "Country not found"})
                data["country"] = country.first()
            if "country_of_work" in data:
                country_of_work = data.get("country_of_work")
                country_of_work = CountryService().filter(Q(name=country_of_work) | Q(code=country_of_work))
                if not country_of_work:
                    return JsonResponse({"code": "999.999.004", "message": "Country of work not found"})
                data["country_of_work"] = country_of_work.first()
            if not ProfileService().update(pk=user.profile.id, **data):
                raise Exception("User profile not updated - user_id: %s data: %s" % (user_id, data))
            return JsonResponse({"code": "100.000.000", "message": "Profile updated successfully"})
        except Exception as e:
            lgr.exception("Update profile exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Update profile failed with an exception"})

    @csrf_exempt
    @user_login_required
    def change_password(self, request):
        """
        Changes a user's password
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
            if not user.check_password(data.get("old_password")):
                response = {"code": "999.999.002", "message": "Wrong password"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            new_password = data.get("password")
            if not new_password:
                response = {"code": "999.999.003", "message": "Password not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            user.set_password(new_password)
            user.save()
            response = {"code": "100.000.000", "message": "Password changed successfully"}
            self.complete_transaction(transaction, response=response)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Update password exception: %s" % e)
            response = {"code": "999.999.999", "message": "Change password failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    @user_login_required
    def reset_password(self, request):
        """
        Resets a users password - Admin side
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
            user.save()
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
    def forgot_password(self, request):
        """
        Resets a users password - Normal user
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("ForgotPassword", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            credential = data.get("credential", "")
            if not credential:
                response = {"code": "999.999.002", "message": "Credential not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            system = data.get("system", "")
            if not system:
                response = {"code": "999.999.003", "message": "System not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            system = SystemService().get(name=system)
            if not system:
                response = {"code": "999.999.004", "message": "Invalid system"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            user = UserService().filter(
                Q(username=credential) | Q(email=credential) | Q(phone_number=credential), systems=system,
                state=State.active())
            if not user:
                response = {"code": "999.999.005", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            user = user.first()
            password = generate_password()
            user.set_password(password)
            user.save()
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
    @user_login_required
    def change_role(self, request):
        """
        Resets a users password
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("ChangeRole", request=request)
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
            if not role:
                response = {"code": "999.999.003", "message": "Role name not provided"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            role = RoleService().get(name=role, state=State.active())
            if not role:
                response = {"code": "999.999.004", "message": "Role provided not valid"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            if not UserService().update(pk=user_id, role=role):
                raise Exception("Role not updated - user_id: %s role_name: %s" % (user_id, role.name))
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

    @csrf_exempt
    @user_login_required
    def update_systems(self, request):
        """
        Removes all systems and adds the provided ones
        @params: WSGI Request
        @return: success or failure message
        @rtype: JsonResponse
        """
        transaction = None
        try:
            transaction = self.log_transaction("UpdateSystems", request=request)
            if not transaction:
                return JsonResponse({"code": "999.999.001", "message": "Transaction not created"})
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                response = {"code": "999.999.002", "message": "User not found"}
                self.mark_transaction_failed(transaction, response=response)
                return JsonResponse(response)
            user.systems.remove(*user.systems.all())
            systems = data.get("systems", [])
            for system in systems:
                s = SystemService().get(name=system)
                if not s:
                    raise Exception("Invalid system - %s" % system)
                user.systems.add(s)
            notification_msg = "Your systems were updated successfully"
            notification_details = create_notification_detail(
                message_code="SC0009", message_type="2", message=notification_msg, destination=user.email)
            response = {"code": "100.000.000", "message": "Systems updated successfully"}
            self.complete_transaction(transaction, response=response, notification_details=notification_details)
            return JsonResponse(response)
        except Exception as e:
            lgr.exception("Update systems exception: %s" % e)
            response = {"code": "999.999.999", "message": "Update systems failed with an exception"}
            self.mark_transaction_failed(transaction, response=response)
            return JsonResponse(response)

    @csrf_exempt
    @user_login_required
    def fetch_user(self, request):
        """
        Fetches details of a user
        @params: WSGI Request
        @return: success message and user details or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            user_id = data.get("user_id", "")
            user = UserService().get(id=user_id, state=State.active())
            if not user:
                return JsonResponse({"code": "999.999.001", "message": "User not found"})
            if user.profile:
                user_data = UserService().filter(id=user_id, state=State.active()) \
                    .annotate(organisation_name=F('organisation__name')).annotate(role_name=F('role__name')) \
                    .annotate(state_name=F('state__name')).annotate(other_phone_number=F('profile__other_phone_number')) \
                    .annotate(id_no=F('profile__id_no')).annotate(occupation=F('profile__occupation')) \
                    .annotate(employment_type=F('profile__employment_type')) \
                    .annotate(income_from_investments=F('profile__income_from_investments')) \
                    .annotate(currency=F('profile__currency')).annotate(net_salary=F('profile__net_salary')) \
                    .annotate(work_place_grants_or_allowance=F('profile__work_place_grants_or_allowance')) \
                    .annotate(physical_work_address=F('profile__physical_work_address')) \
                    .annotate(country=F('profile__country__name')) \
                    .annotate(country_of_work=F('profile__country_of_work__name')).values(
                    'username', 'email', 'phone_number', 'first_name', 'last_name', 'other_name', 'gender',
                    'organisation_name', 'is_superuser', 'role_name', 'terms_and_conditions_accepted', 'language_code',
                    'last_activity', 'state_name', 'id_no', 'other_phone_number', 'occupation', 'employment_type',
                    'income_from_investments', 'currency', 'net_salary', 'work_place_grants_or_allowance',
                    'physical_work_address', 'country', 'country_of_work').first()
            else:
                user_data = UserService().filter(id=user_id, state=State.active()) \
                    .annotate(organisation_name=F('organisation__name')).annotate(role_name=F('role__name')) \
                    .annotate(state_name=F('state__name')).values(
                    'username', 'email', 'phone_number', 'first_name', 'last_name', 'other_name', 'gender',
                    'organisation_name', 'is_superuser', 'role_name', 'terms_and_conditions_accepted', 'language_code',
                    'last_activity', 'state_name').first()
            user_data.update({"permissions": user.get_permissions})
            return JsonResponse({"code": "100.000.000", "message": "Successfully fetched user data", "data": user_data})
        except Exception as e:
            lgr.exception("Fetch user exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Fetch user failed with an exception"})

    @csrf_exempt
    def fetch_users(self, request):
        """
        Fetches details of filtered users
        @params: WSGI Request
        @return: success message and user details or failure message
        @rtype: JsonResponse
        """
        try:
            data = get_request_data(request)
            system = data.pop("system", "")
            data.pop("source_ip", "")
            data.pop("token", "")
            if not system:
                return JsonResponse({"code": "999.999.001", "message": "System not provided"})
            system = SystemService().get(name=system)
            if not system:
                return JsonResponse({"code": "999.999.002", "message": "Invalid system"})
            if "organisation" in data:
                organisation = data.get("organisation")
                organisation = OrganisationService().filter(
                    Q(name=organisation) | Q(remote_code=Organisation), state=State.active())
                if not organisation:
                    return JsonResponse({"code": "999.999.002", "message": "Invalid organisation"})
                data["organisation"] = organisation.first()
            if "role" in data:
                role = data.get("role")
                role = RoleService().get(name=role, state=State.active())
                if not role:
                    return JsonResponse({"code": "999.999.003", "message": "Invalid role"})
                data["role"] = role
            users_data = []
            if UserService().filter(**data, systems=system, state=State.active()):
                users_data = UserService().filter(**data, systems=system, state=State.active()) \
                    .annotate(organisation_name=F('organisation__name')).annotate(role_name=F('role__name')) \
                    .annotate(state_name=F('state__name')) \
                    .annotate(other_phone_number=F('profile__other_phone_number')) \
                    .annotate(id_no=F('profile__id_no')).annotate(occupation=F('profile__occupation')) \
                    .annotate(employment_type=F('profile__employment_type')) \
                    .annotate(income_from_investments=F('profile__income_from_investments')) \
                    .annotate(currency=F('profile__currency')).annotate(net_salary=F('profile__net_salary')) \
                    .annotate(work_place_grants_or_allowance=F('profile__work_place_grants_or_allowance')) \
                    .annotate(physical_work_address=F('profile__physical_work_address')) \
                    .annotate(country=F('profile__country__name')) \
                    .annotate(country_of_work=F('profile__country_of_work__name')).values(
                    'id', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'other_name', 'gender',
                    'organisation_name', 'is_superuser', 'role_name', 'terms_and_conditions_accepted', 'language_code',
                    'last_activity', 'state_name', 'id_no', 'other_phone_number', 'occupation', 'employment_type',
                    'income_from_investments', 'currency', 'net_salary', 'work_place_grants_or_allowance',
                    'physical_work_address', 'country', 'country_of_work')
            return JsonResponse(
                {"code": "100.000.000", "message": "Successfully fetched user data", "data": list(users_data)})
        except Exception as e:
            lgr.exception("Fetch user exception: %s" % e)
            return JsonResponse({"code": "999.999.999", "message": "Fetch user failed with an exception"})
