.. |mnt| replace:: Django Site Maintenance
.. _index:

=======================
Django Site Maintenance
=======================

:Date: |today|

Overview
--------

|mnt| is a site maintenance library that allow you to put your `Django <http://www.djangoproject.com>`_ site 'offline'.
It's  work at web-server level so it's possible to completely shutting-down your django application.

The webserver is configured to redirect all the request to alternative url,
if some condition is verified true. Anyway before activate the redirection |mnt| will wait for
all logged users exit and do not allow new user to logging in.
Active users can be informed of the oncoming system shutdown by a on scree message.


Table Of Contents
-----------------

.. toctree::
    :maxdepth: 2

    install
    components
    api


Links
~~~~~

   * Project home page: https://github.com/saxix/django-iadmin
   * Issue tracker: https://github.com/saxix/django-iadmin/issues?sort
   * Download: http://pypi.python.org/pypi/django-iadmin/
   * Docs: http://readthedocs.org/docs/django-iadmin/en/latest/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
