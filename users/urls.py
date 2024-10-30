from django.urls import re_path

from users.views import UsersAdministration

urlpatterns = [
    re_path(r'^create-user/$', UsersAdministration().create_user),
    re_path(r'^delete-user/$', UsersAdministration().delete_user),
    re_path(r'^update-personal-details/$', UsersAdministration().update_personal_details),
    re_path(r'^update-profile/$', UsersAdministration().update_profile),
    re_path(r'^change-password/$', UsersAdministration().change_password),
    re_path(r'^reset-password/$', UsersAdministration().reset_password),
    re_path(r'^forgot-password/$', UsersAdministration().forgot_password),
    re_path(r'^update-systems/$', UsersAdministration().update_systems),
    re_path(r'^change-role/$', UsersAdministration().change_role),
    re_path(r'^fetch-user/$', UsersAdministration().fetch_user),
    re_path(r'^fetch-users/$', UsersAdministration().fetch_users),
]