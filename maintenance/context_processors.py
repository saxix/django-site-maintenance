from django.utils.translation import gettext as _
from maintenance import api

def maintenance():
    return {'maintenance_status': api.status()}