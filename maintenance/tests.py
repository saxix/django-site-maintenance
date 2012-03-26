from django.conf import settings
from django.core.management import call_command
from django.utils.unittest.case import TestCase
import os

class Test(TestCase):


    def test_activate_deactivate(self):
        call_command('offline', 'activate')
        self.assertTrue(os.path.exists(settings.MAINTENANCE_FILE))
        call_command('offline', 'deactivate')
        self.assertFalse(os.path.exists(settings.MAINTENANCE_FILE))
