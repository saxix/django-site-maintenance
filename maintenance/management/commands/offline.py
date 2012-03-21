from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
import maintenance.api as api
import logging

logger = logging.getLogger("maintenance")


class Command(LabelCommand):
    option_list = LabelCommand.option_list + (make_option('--force', action='store_true', dest='ignore_session', default=False,
        help='Do not wiat for active session. Brutally disconnect users'),)

    args = 'on|off|check'
    label = 'command'
    help = """ """


    def handle_default_options(self):
        pass

    def handle_label(self, cmd, **options):
        if cmd not in ('on', 'off', 'check'):
            raise CommandError('Allowed options are: %s' % self.args)

        if cmd == 'check':
            print "Status: %s - Active sessions: %s" % ( api.STATUS._labels[api.status()], api.get_active_users())
        elif cmd == 'on':
            ignore_session = options.get('ignore_session')
            api.start(ignore_session)
        elif cmd == 'off':
            api.stop()






