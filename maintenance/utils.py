import logging
from django.conf import settings
from django.utils.importlib import import_module
from maintenance import api
from maintenance.api import MaintenanceModeError
from maintenance.management.lockfile import FileLock, LockFailed, AlreadyLocked, LockTimeout, NotLocked
import signal

__all__ = ['register_session', 'unregister_session', 'CommandTask', 'CommandRunningError']
logger = logging.getLogger("commands")

class CommandRunningError(Exception):
    pass


def register_session(session_key):
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(session_key)
    if session.exists(session_key):
        raise CommandRunningError()
    session.create()


def unregister_session(session_key):
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(session_key)
    session.delete()


def fmt_duration(secs):
    pluralize = lambda value, label: "%s%s" % (label, ['','s'][value>1])
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    ret = []
    if hours > 0:
        ret.append(str(int(hours)))
        l = pluralize(hours, "hour")
    if minutes or (seconds and hours):
        ret.append(str(int(minutes)))
        l = pluralize(minutes, "minute")
    if seconds:
        ret.append(str(int(seconds)))
        l = pluralize(seconds, "second")
    return "%s %s " %  (":".join(ret), l)

def cleanup_factory(owner):
    def _inner(*args):
        return owner.cleanup(*args)
    return _inner

class CommandTask(object):
    """
        Context Manager to handle both parallel running and maintenance mode, it:
          - do not allow to run two django command wir the same ``session_key``
          - do not allow to run the command if Maintenance-mode is active/pending

           session_key        id of current command
           force              if True ignore lock and run in parralel, if any
           timeout            timeout for locking release
           check_maintenance  check Maintenance mode
    """
    def  __init__( self, session_key, force=False, timeout=1, check_maintenance=False):
        self._key = "%s.lock" % session_key
        self.lock = FileLock(self._key)

        if check_maintenance:
            if api.is_pending() or api.is_offline():
                raise MaintenanceModeError('Maintenance mode activated')

        if force:
            self.lock.break_lock()
        try:
            self.lock.acquire(timeout)
        except (AlreadyLocked, LockFailed, LockTimeout), e:
            raise CommandRunningError('Unable to lock', e)

    def cleanup(self, type=None, value=None, tb=None):
        try:
            self.lock.release()
        except NotLocked:
            pass
        unregister_session(self._key)
        if type:
            logger.exception(value)
            raise type(value)

    def __enter__( self ):
        try:
            register_session(self._key)
        except:
            self.lock.release()
            raise
        return self

    def __exit__( self, type, value, tb ):
        self.cleanup(type, value, tb )
