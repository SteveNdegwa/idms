from django.urls import re_path, include

from api.views import APIManager

urlpatterns = [
    re_path(r'^create-api-user/', APIManager().create_api_user),
    re_path(r'^refresh-api-keys/', APIManager().refresh_api_keys),
    re_path(r'^users/', include('users.urls')),
    re_path(r'^organisations/', include('organisations.urls')),
    re_path(r'^systems/', include('systems.urls')),
    re_path(r'^integration-apps/', include('integration_apps.urls')),
    re_path(r'^identities/', include('identities.urls')),
]