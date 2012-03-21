from django.http import HttpResponseRedirect
from maintenance import api



class MaintenanceMiddleware(object):

    def process_request(self, request):
        if api.MAINTENANCE_URL == request.path:
            return None

        if api.is_active() or api.is_pending():
            return HttpResponseRedirect(api.MAINTENANCE_URL)

        return None
