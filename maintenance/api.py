import itertools
import os, sys
from time import sleep
import time
from types import *
from django.templatetags.static import static
from django.conf import settings
from django.utils import timezone

def enum(**enums):
    enums['_labels'] = dict(zip(enums.values(), map(str.upper, enums.keys())))
    return type('Enum', (), enums)

STATUS = enum(STARTED=1, PENDING=2, OFFLINE=3, STOPPED=4)
MAINTENANCE_FILE = getattr(settings, 'MAINTENANCE_FILE', '/tmp/MAINTENANCE_FILE_%s' % settings.SITE_ID)
PENDING_MAINTENANCE_FILE = "%s_" % MAINTENANCE_FILE

MAINTENANCE_URL = getattr(settings, 'MAINTENANCE_URL', static('maintenance/maintenance.html'))


def start(ignore_session=False):
    """ activate maintenance mode.
    this not mean that the application will be down. Check `is_active` for that.
    Logged users continue to work but no other logins will be allowed
    """
    C = ['*', '-']
    rounds = 0
    open(PENDING_MAINTENANCE_FILE, 'w').close()
    if not ignore_session:
        try:
            _start = time.time()
            while True:
                users = get_active_users()
                if not users:
                    break
                if not rounds:
                    print "Active sessions detected. Waiting for logout. (Session timeout set to %s secs) " % settings.SESSION_COOKIE_AGE
                rounds += 1
                sys.stdout.write("%s pending sessions. %s (%d sec)\r" % (users, C[rounds % 2], round(time.time()-_start)))
                sys.stdout.flush()
                sleep(1)
        except KeyboardInterrupt:
            print 'Interrupt'
            return

    open(MAINTENANCE_FILE, 'w').close()
    os.unlink(PENDING_MAINTENANCE_FILE)
    print is_active()

def stop():
    if os.path.isfile(MAINTENANCE_FILE):
        os.unlink(MAINTENANCE_FILE)

    if os.path.isfile(PENDING_MAINTENANCE_FILE):
        os.unlink(PENDING_MAINTENANCE_FILE)
    print is_active()

def get_active_users():
    from django.db import transaction
    from django.contrib.sessions.models import Session

    Session.objects.filter(expire_date__lt=timezone.now()).delete()
    transaction.commit_unless_managed()
    return Session.objects.count()


def is_started():
    """ true if maintenance mode is started."""
    return os.path.exists(MAINTENANCE_FILE)


def is_pending():
    """ true if maintenance mode is pending. ie. wait for active session to expire """
    return os.path.exists(PENDING_MAINTENANCE_FILE) or os.path.exists(MAINTENANCE_FILE)


def is_active():
    """ true if maintenance mode is on
    """
    return os.path.exists(MAINTENANCE_FILE) and get_active_users() == 0


def is_stopped():
    """ true if maintenance mode is off """
    return not is_active()


def status():
    if is_active():
        return STATUS.ACTIVE
    elif is_pending():
        return STATUS.PENDING
    elif is_stopped():
        return STATUS.STOPPED
    elif is_started():
        return STATUS.STARTED


