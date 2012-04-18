.. |mnt| replace:: Django Site Maintenance
.. |pkg| replace:: maintenance

.. _components:

Components
==========
This section describe the componenets of |mnt|

- offline command
- MaintenanceMiddleware
- maintenance
- CommandTask



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

.. _option_status:

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
This middleware intercept the request and redirect to the ``MAINTENANCE_URL`` with this policy:

    * State: is_pending()
        - Logged user are allowed to work. :ref:`maintenance.context_processors.maintenance` should be used to inform them for the pending offline mode
        - New user's requests will bre redirectd to ``MAINTENANCE_URL``

    * State: is_offline()
        - Nobody will be able to access to the site.

    .. note:: In normal condition if the status is offline the middleware code should never be executed because web server redirect rule should intercept the request



.. _maintenance.context_processors.maintenance:

The ``maintenance`` context-processor
--------------------------------------
    simply returns the status :ref:`option_status`


CommandTask
-----------
    You should not shutdown your application if any user is logged  in or any command
    running on so this context manager that allow to register a new session
    for the current command so that will be possible to check for
    running commands as for logged user.

    how to use it::

        def handle(self, *args, **options):
            with CommandTask("mycommand", force=False, timeout=timeout):
                ...
                ...


