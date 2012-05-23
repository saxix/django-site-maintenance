from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.importlib import import_module
from maintenance import api
import logging

logger = logging.getLogger("maintenance.middleware")

class MaintenanceMiddleware(object):
    def redirect(self, status):
        logger.info('Maintenance Mode: Status %s. Redirect to %s' % (status, api.MAINTENANCE_URL))
        return HttpResponseRedirect(api.MAINTENANCE_URL)

    def process_request(self, request):
        if api.MAINTENANCE_URL == request.path:
            return None

        status = api.status()

        if status == api.STATUS.OFFLINE:
            return self.redirect(api.STATUS.OFFLINE)

        if  status == api.STATUS.PENDING:
            engine = import_module(settings.SESSION_ENGINE)
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
            session = engine.SessionStore()
            if session.exists(session_key):
                return None
            else:
                return self.redirect(api.STATUS.PENDING)

        return None
