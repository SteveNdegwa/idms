import logging
import base64

from django.http import JsonResponse

from api.backend.services import APIUserService

lgr = logging.getLogger(__name__)

def AuthorizeMiddleware(get_response):
    try:
        def middleware(request):
            url_whitelist = ["/api/generate-token/"]
            if not str(request.get_full_path()).startswith("/api") or request.get_full_path() in url_whitelist:
                return get_response(request)
            auth_token = request.headers.get("Authorization", "")
            if auth_token:
                auth_token = auth_token.split()
                if auth_token[0] == "Basic":
                    username, password = (base64.b64decode(auth_token[1])).decode("utf-8").split(':')
                    user = APIUserService().get(username=username)
                    if user and user.check_password(password):
                        return get_response(request)
            return JsonResponse({"code": "888.888.888", "message": "Not Authorized"})
        return middleware
    except Exception as ex:
        lgr.exception("AuthorizeMiddleware exception: %s" % ex)
        return JsonResponse({"code": "888.888.888", "message": "Not Authorized"})