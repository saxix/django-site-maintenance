
.. |mnt| replace:: Django Site Maintenance
.. |pkg| replace:: maintenance



Installation
============

In order to install |mnt| simply use ``pip``::

   pip install django-site-maintenance

or ``easy_install``::

   easy_install django-site-maintenance


Configuration
=============

After installation add |pkg| to ``INSTALLED_APPS``::

   INSTALLED_APPS = (
       # ...
       'maintenance',
   )

   MIDDLEWARE_CLASSES = (
        'maintenance.middleware.MaintenanceMiddleware'
        # ...
   )

Also configure the file lock location::

    MAINTENANCE_FILE = '/absolute/path/to/file'


.. note::
    MAINTENANCE_FILE must be read accessible by your web server user.


Optionally set::

    MAINTENANCE_URL='url/where/redirect/during/maintenance'



.. note::
    The standard location of the `MAINTENANCE_URL` is ::doc::STATIC_URL/maintenance/maintenance.html

Configuring Web server
----------------------

Apache
~~~~~~
::

    RewriteEngine On
    RewriteCond $MAINTENANCE_FILE -f
    RewriteCond %{REQUEST_URI} !/$STATIC_URL/maintenance/under-maintenance.gif
    RewriteRule ^(.+) $MAINTENANCE_URL [RL]


NGNIX
~~~~~~
::

     if (-f $MAINTENANCE_FILE ) {
        if ($request_uri !~* "$STATIC_URL/maintenance/under-maintenance.gif$"){
            rewrite  (.*)  $MAINTENANCE_URL;
        }
     }

Others
~~~~~~

Please let me know opening a ticket at https://github.com/saxix/django-site-maintenance/issues

