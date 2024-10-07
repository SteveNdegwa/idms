from django.urls import re_path

from identities.views import IdentitiesAdministration

urlpatterns = [
    re_path(r'^login/$', IdentitiesAdministration().login),
    re_path(r'^verify/$', IdentitiesAdministration().verify_totp),
    re_path(r'^logout/$', IdentitiesAdministration().logout),
]