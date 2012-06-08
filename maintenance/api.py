import logging
import datetime
#from django.utils import timezone
import os, sys
from time import sleep
import time
from types import *
from maintenance.models import MaintenanceWindow

try:
    from django.templatetags.static import static
except ImportError: # 1.3 fallback
    from urlparse import urljoin

    def static(path):
        return urljoin(settings.STATIC_URL, path)

from django.conf import settings

logger = logging.getLogger("maintenance")

def enum(**enums):
    enums['_labels'] = dict(zip(enums.values(), map(str.upper, enums.keys())))
    return type('Enum', (), enums)

STATUS = enum(OFFLINE=2, PENDING=3, ONLINE=4)
MAINTENANCE_FILE = getattr(settings, 'MAINTENANCE_FILE', '/tmp/DJANGO_MAINTENANCE_FILE_%s' % settings.SITE_ID)
PENDING_MAINTENANCE_FILE = "%s_" % MAINTENANCE_FILE
MAINTENANCE_URL = getattr(settings, 'MAINTENANCE_URL', static('maintenance/maintenance.html'))

SUCCESS = 0
ERROR_BREAK = 1
ERROR_TIMEOUT = 2
ERROR_GENERIC = 3

class MaintenanceModeError(Exception):
    pass


def start(ignore_session=False, timeout=60, verbosity=1):
    """ activate maintenance mode.
    this not mean that the application will be down. Check `is_active` for that.
    Logged users continue to work but no other logins will be allowed
    """
    C = ['*', '-']
    rounds = 0
    code = ERROR_GENERIC
    logger.info('Maintenance mode start pending')
    open(PENDING_MAINTENANCE_FILE, 'w').close()
    if not ignore_session:
        try:
            _start = time.time()
            while True:
                users = get_active_users()
                if not users:
                    break
                if not rounds:
                    if verbosity > 0:
                        print "Active sessions detected. Waiting for logout. (Session timeout set to %s secs) " % settings.SESSION_COOKIE_AGE
                        print "Type double ^C to stop"
                        sys.stdout.write(
                            "%s pending sessions. %s (%d sec)\r" % (users, C[rounds % 2], round(time.time() - _start)))
                        sys.stdout.flush()
                rounds += 1
                if rounds >= timeout:
                    return ERROR_TIMEOUT, '\nTimeout'
                sleep(1)
        except KeyboardInterrupt:
            return ERROR_BREAK, '\nInterrupt'
        finally:
            if os.path.isfile(PENDING_MAINTENANCE_FILE):
                os.unlink(PENDING_MAINTENANCE_FILE)

    open(MAINTENANCE_FILE, 'w').close()
    logger.info('Maintenance mode started')
    return SUCCESS, 'Maintenance mode started'


def check():
    return 0, "Status: %s - Active sessions: %s" % ( STATUS._labels[status()], get_active_users())


def stop():
    if os.path.isfile(MAINTENANCE_FILE):
        os.unlink(MAINTENANCE_FILE)

    if os.path.isfile(PENDING_MAINTENANCE_FILE):
        os.unlink(PENDING_MAINTENANCE_FILE)
    logger.info('Maintenance mode stop')
    return 0, 'Maintenance mode stop'


def get_active_users():
    from django.db import transaction
    from django.contrib.sessions.models import Session

    Session.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
    transaction.commit_unless_managed()
    return Session.objects.count()


def is_offline():
    """ true if maintenance mode is started."""
    return os.path.exists(MAINTENANCE_FILE)


def is_pending():
    """ true if maintenance mode is pending. ie. wait for active session to expire """
    return os.path.exists(PENDING_MAINTENANCE_FILE) and not os.path.exists(MAINTENANCE_FILE)


def is_online():
    """ true if maintenance mode is off """
    return not is_offline()


def status():
#    if MaintenanceWindow.objects.actives():
#        return STATUS.SOFT

    if is_offline():
        return STATUS.OFFLINE
    elif is_pending():
        return STATUS.PENDING
    elif is_online():
        return STATUS.ONLINE


