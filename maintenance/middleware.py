from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from maintenance import api



class MaintenanceMiddleware(object):

    def process_request(self, request):
        if api.MAINTENANCE_URL == request.path:
            return None

        if api.is_offline():
            return HttpResponseRedirect(api.MAINTENANCE_URL)

        if  api.is_pending():
            engine = import_module(settings.SESSION_ENGINE)
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
            session = engine.SessionStore()
            if session.exists(session_key):
                return

        return None
