import logging
from django.conf import settings
from django.utils.importlib import import_module
from maintenance.management.lockfile import FileLock, LockFailed, AlreadyLocked, LockTimeout

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

class CommandTask( object ):
    def __init__( self, session_key, force=False, timeout=1 ):
        self._key= session_key
        self.lock = FileLock(self._key)

        if force:
            self.lock.break_lock()

        try:
            self.lock.acquire(timeout)
        except (AlreadyLocked, LockFailed, LockTimeout), e:
            raise CommandRunningError('Unable to lock', e)

    def __enter__( self ):
        register_session(self._key)

    def __exit__( self, type, value, tb ):
        self.lock.release()
        unregister_session(self._key)
        if type:
            logger.exception(value)
            raise type(value)
