from datetime import datetime
from django.db import models
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _

class MaintenanceWindowManager(Manager):

    def actives(self):
        """ returns true if there
        """
        now = datetime.now()
        return MaintenanceWindow.objects.filter(start_date__lt=now, end_date__gt=now, mode=MaintenanceWindow.MODE_SOFT).exists()


class MaintenanceWindow(models.Model):
    MODE_FULL = 1
    MODE_SOFT = 2
    MODES = ((MODE_FULL, _('Full offline mode. Project is disconnected')),
             (MODE_FULL, _('Soft offline mode. Admins are allowed to login')),)

    name = models.CharField(_('Maintenance Name'), max_length=255)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    mode = models.IntegerField(choices=MODES)
    notificiation_period = models.IntegerField(_('Notification Period'), help_text='Notification period before maintenance (in minutes)')

    notify_users = models.BooleanField(default=False)

    objects = MaintenanceWindowManager()

    def __unicode__(self):
        return self.name
