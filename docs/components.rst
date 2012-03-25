.. |mnt| replace:: Django Site Maintenance
.. |pkg| replace:: maintenance

.. _components:

Components
==========
This section describe the componenets of |mnt|

- offline command
- MaintenanceMiddleware
- maintenance




The ``offline`` command
-----------------------

The commannd ``activate``, ``deacttivate``, ``check`` the offline status.::

$ django-admin.py offline (activate|deactivate|status) [--force]


.. option:: activate, on

    activate the offline mode.

.. note::
    this do not put the site in maintenance mode immediately but wait until all active sessions expire

.. option:: deactivate, off

    deactivate maintenance mode

.. option:: status, check

    check the status of maintenance mode. Possible feedbacks are:


    * ONLINE: The system is on line

    * PENDING: Offline mode as been requested but not still active.< No other users can login, but active sessions can still work on site. ( see :option:`--force` below)

    * OFFLINE: The system is offline


Options
^^^^^^^

.. option:: --force

    Do not wait for sessions expiration  but immmedialetly enable the offline mode.


*Examples*::

    $ ./manage.py offline check
    Status: ONLINE - Active sessions: 13

    $ ./manage.py offline on
    Active sessions detected. Waiting for logout. (Session timeout set to 900 secs)
    5 pending sessions. * (3 sec)

    $ ./manage.py offline on --force
    Status: OFFLINE - Active sessions: 1


MaintenanceMiddleware
---------------------

TODO

The ``maintenance`` context-processor
--------------------------------------

TODO

