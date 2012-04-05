.. |mnt| replace:: Django Site Maintenance
.. _api:

API
===

.. autofunction:: maintenance.api.start

.. autofunction:: maintenance.api.stop

.. autofunction:: maintenance.api.check

.. autofunction:: maintenance.api.get_active_users

.. autofunction:: maintenance.api.is_offline

.. autofunction:: maintenance.api.is_pending

.. autofunction:: maintenance.api.is_online

.. autofunction:: maintenance.api.status


.. autofunction:: maintenance.context_processors.maintenance

.. autoclass:: maintenance.middleware.MaintenanceMiddleware

.. autoclass:: maintenance.utils.CommandTask
