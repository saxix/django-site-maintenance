import os
from time import sleep
import time
from types import *
from django.templatetags.static import static
from django.conf import settings

def enum(**enums):
    enums['_labels'] = dict(zip(enums.values(), map(str.upper, enums.keys())))
    return type('Enum', (), enums)

STATUS = enum(STARTED=1, OFFLINE=2, ONLINE=4)
MAINTENANCE_FILE = getattr(settings, 'MAINTENANCE_FILE', '/tmp/DJANGO_MAINTENANCE_FILE_%s' % settings.SITE_ID)
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
                sys.stdout.write(
                    "%s pending sessions. %s (%d sec)\r" % (users, C[rounds % 2], round(time.time() - _start)))
                sys.stdout.flush()
                sleep(1)
        except KeyboardInterrupt:
            print 'Interrupt'
            return
        finally:
            os.unlink(PENDING_MAINTENANCE_FILE)

    open(MAINTENANCE_FILE, 'w').close()
    check()


def check():
    print "Status: %s - Active sessions: %s" % ( STATUS._labels[status()], get_active_users())


def stop():
    if os.path.isfile(MAINTENANCE_FILE):
        os.unlink(MAINTENANCE_FILE)

    if os.path.isfile(PENDING_MAINTENANCE_FILE):
        os.unlink(PENDING_MAINTENANCE_FILE)
    check()


def get_active_users():
    from django.db import transaction
    from django.contrib.sessions.models import Session

    Session.objects.filter(expire_date__lt=timezone.now()).delete()
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
    if is_offline():
        return STATUS.OFFLINE
    elif is_pending():
        return STATUS.PENDING
    elif is_online():
        return STATUS.ONLINE


