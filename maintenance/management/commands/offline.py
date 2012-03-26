from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
import maintenance.api as api
import logging

logger = logging.getLogger("maintenance")


class Command(LabelCommand):
    option_list = LabelCommand.option_list + (
        make_option('--force', action='store_true', dest='ignore_session', default=False,
            help='Do not wait for active session. Brutally disconnect users'),

        make_option('--timeout', action='store', dest='timeout', default=60,
            help='Time to wait for pending sessions'),)

    args = 'on|off|check'
    label = 'command'
    help = """ """


    def handle_default_options(self):
        pass

    def handle_label(self, cmd, **options):
        verbosity = options.get('verbosity')
        timeout = options.get('timeout')
        ignore_session = options.get('ignore_session')

        if cmd not in ('on', 'off', 'check', 'activate', 'deactivate', 'status'):
            raise CommandError('Allowed options are: %s' % self.args)

        if cmd in ('check', 'status'):
            print api.check()
        elif cmd in ('on', 'activate'):
            api.start(ignore_session, timeout, verbosity)
            if verbosity >= 1:
                print api.check()
        elif cmd in ('off', 'deactivate'):
            api.stop()
            if verbosity >= 1:
                print api.check()






