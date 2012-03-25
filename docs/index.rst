.. |mnt| replace:: Django Site Maintenance
.. _index:


Django Site Maintenance
=======================

:Date: |today|

|mnt| is a site maintenance library that allow you to put your `Django <http://www.djangoproject.com>`_ site 'offline'.
It's  work at web-server level so it's possible to completely shutting-down your django application.

The webserver is configured to redirect all the request to alternative url,
if some condition is verified true. Anyway before activate the redirection |mnt| will wait for
all logged users exit and do not allow new user to logging in.
Active users can be informed of the oncoming system shutdown by a on scree message.


.. toctree::
    :maxdepth: 2

    install
    components
    api

Links
-----

   * Code: http://github.com/saxix/django-site-maintenance
   * Docs: http://readthedocs.org/docs/django-site-maintenance/en/latest/index.html


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
