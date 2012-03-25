from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.importlib import import_module
from maintenance import api



class MaintenanceMiddleware(object):
    """ this middleware intercept the request and redirect ``MAINTENANCE_URL`` with this policy:

    * State: is_pending()
        - Logged user are allowed to work. :ref:`maintenance.context_processors.maintenance` should be used to inform them for the pending offline mode
        - New user's requests will bre redirectd to ``MAINTENANCE_URL``

    * State: is_offline()
        - Nobody will be able to access to the site, but it's only a double chyou should  not be here
    """

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
