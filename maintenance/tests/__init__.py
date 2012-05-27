import logging
from django.core.files import temp
from django.core.management import call_command
from django.test.testcases import TestCase
import os
import time
from maintenance import api, middleware
from maintenance.tests.future import SimpleTestCase

class MaintenanceTestCaseMixIn(object):

    def log_to_console(self):
    #        logging.disable(logging.CRITICAL)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        consoleLogger = logging.StreamHandler()
        consoleLogger.setLevel(logging.DEBUG)
        consoleLogger.setFormatter(formatter)

        rootLogger = logging.getLogger()
        rootLogger.addHandler(consoleLogger)
        rootLogger.setLevel(logging.NOTSET)

        api.logger.setHandler(consoleLogger)
        middleware.logger.setHandler(consoleLogger)
        api.logger.setLevel(logging.DEBUG)
        middleware.logger.setLevel(logging.DEBUG)


    def setUp(self):
        api.MAINTENANCE_FILE = temp.NamedTemporaryFile('rw', delete=False).name
        api.PENDING_MAINTENANCE_FILE = "%s_" % api.MAINTENANCE_FILE
        self.log_to_console()

    def tearDown(self):
        api.stop()


class TestCommand(TestCase, MaintenanceTestCaseMixIn):
    def test_activate_deactivate(self):
        call_command('offline', 'activate')
        self.assertTrue(os.path.exists(api.MAINTENANCE_FILE))
        call_command('offline', 'deactivate')
        self.assertFalse(os.path.exists(api.MAINTENANCE_FILE))

    def test_activate_deactivate(self):
        call_command('offline', 'activate', verbosity=0)
        self.assertTrue(os.path.exists(api.MAINTENANCE_FILE))
        call_command('offline', 'deactivate', verbosity=0)
        self.assertFalse(os.path.exists(api.MAINTENANCE_FILE))


class TestAPI(TestCase, MaintenanceTestCaseMixIn):
    def test_start(self):
        api.start()
        self.assertTrue(os.path.exists(api.MAINTENANCE_FILE))
        self.assertFalse(os.path.exists(api.PENDING_MAINTENANCE_FILE))

    def test_stop(self):
        api.stop()
        self.assertFalse(os.path.exists(api.MAINTENANCE_FILE))
        self.assertFalse(os.path.exists(api.PENDING_MAINTENANCE_FILE))

    def test_is_online(self):
        api.start()
        self.assertFalse(api.is_online())
        api.stop()
        self.assertTrue(api.is_online())


class TestMiddleware(SimpleTestCase, MaintenanceTestCaseMixIn):
    fixtures = ['sax.json', ]
    urls = 'maintenance.tests.test_urls'
    MIDDLEWARE_CLASSES = ['django.contrib.sessions.middleware.SessionMiddleware',
                          'django.contrib.auth.middleware.AuthenticationMiddleware',
                          'maintenance.middleware.MaintenanceMiddleware',
                          ]
    INSTALLED_APPS = ['django.contrib.auth',
                      'django.contrib.contenttypes',
                      'django.contrib.sites',
                      'django.contrib.admin',
                      'django.contrib.sessions']


    def _activate(self, **kwargs):
        from multiprocessing import Process

        kwargs.setdefault('verbosity', 0)
        kwargs.setdefault('timeout', 10)
        p = Process(target=api.start, kwargs=kwargs)
        p.start()
        time.sleep(5)

    def test_logged_user_allowed(self):
        with self.settings(
            MIDDLEWARE_CLASSES=TestMiddleware.MIDDLEWARE_CLASSES,
            INSTALLED_APPS=TestMiddleware.INSTALLED_APPS):
            api.stop() # just to be sure
            assert api.is_online()
            self.client.login(**{'username': 'sax', 'password': '123'})
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 200)
            self._activate()
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 200)

    def test_logged_user_forced(self):
        # not sure this is required
        # web server should itercept request first
        # in any case double check
        with self.settings(
            MIDDLEWARE_CLASSES=TestMiddleware.MIDDLEWARE_CLASSES,
            INSTALLED_APPS=TestMiddleware.INSTALLED_APPS
        ):
            api.stop() # just to be sure
            assert api.is_online()
            self.client.login(**{'username': 'sax', 'password': '123'})
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 200)
            self._activate(ignore_session=True)
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 302)

    def test_new_user_redirected(self):
        with self.settings(MIDDLEWARE_CLASSES=self.MIDDLEWARE_CLASSES, INSTALLED_APPS=self.INSTALLED_APPS):
            self._activate(verbosity=1)
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 302)
