import os
from time import sleep
from types import *
from django.templatetags.static import static
from django.conf import settings
from django.utils import timezone

def enum(**enums):
    enums['_labels'] = dict(zip(enums.values(), enums.keys()))
    return type('Enum', (), enums)

STATUS = enum(STARTED=1, PENDING=2, ACTIVE=3, STOPPED=4)
MAINTENANCE_FILE = getattr(settings, 'MAINTENANCE_FILE', '/tmp/MAINTENANCE_FILE_%s' % settings.SITE_ID)
PENDING_MAINTENANCE_FILE = "%s_" % MAINTENANCE_FILE

MAINTENANCE_URL = getattr(settings, 'MAINTENANCE_URL', static('maintenance/maintenance.html'))


def start(ignore_session=False):
    """ activate maintenance mode.
    this not mean that the application will be down. Check `is_active` for that.
    Logged users continue to work but no other logins will be allowed
    """
    rounds = 0
    users = get_active_users()
    open(PENDING_MAINTENANCE_FILE, 'w').close()
    if not ignore_session:
        while True:
            users = get_active_users()
            if users == 0:
                break
            if rounds == 0:
                print "Active sessions detected. Waiting for logout. (Session timeout set to %s secs) " % settings.SESSION_COOKIE_AGE
            rounds += 1
            sys.stdout.write("%s" % ('.' * rounds))
            sys.stdout.flush()
            sleep(5)

    open(MAINTENANCE_FILE, 'w').close()
    os.unlink(PENDING_MAINTENANCE_FILE)


def stop():
    if os.path.isfile(MAINTENANCE_FILE):
        os.unlink(MAINTENANCE_FILE)

    if os.path.isfile(PENDING_MAINTENANCE_FILE):
        os.unlink(PENDING_MAINTENANCE_FILE)


def get_active_users():
    from django.db import transaction
    from django.contrib.sessions.models import Session

    Session.objects.filter(expire_date__lt=timezone.now()).delete()
    transaction.commit_unless_managed()
    return Session.objects.count()


def is_started():
    return os.path.exists(MAINTENANCE_FILE)


def is_pending():
    return os.path.exists(PENDING_MAINTENANCE_FILE) or os.path.exists(MAINTENANCE_FILE)


def is_active():
    return os.path.exists(MAINTENANCE_FILE) and get_active_users() == 0


def is_stopped():
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


