.. image:: https://travis-ci.org/liminspace/django-mjml.svg?branch=develop
 :target: https://travis-ci.org/liminspace/django-mjml
 :alt: CI

.. image:: https://img.shields.io/pypi/dm/django-mjml.svg
 :target: https://pypi.python.org/pypi/django-mjml/
 :alt: Downloads

|

.. image:: https://cloud.githubusercontent.com/assets/5173158/14615647/5fc03bf8-05af-11e6-8cdd-f87bf432c4a2.png
  :target: #
  :alt: Django + MJML

django-mjml
===========

The simplest way to use `MJML <https://mjml.io/>`_ in `Django <https://www.djangoproject.com/>`_ templates.

|

Installation
------------

**Requirements:**

* Django v1.8+
* mjml v2.0+

**\1\. Install** ``mjml``.

See https://github.com/mjmlio/mjml#installation and https://mjml.io/documentation/#installation

**\2\. Install** ``django-mjml``.

* Via pip::

  $ pip install django-mjml

* Via setuptools::

  $ easy_install django-mjml
  

 For install development version use ``git+https://github.com/liminspace/django-mjml.git@develop`` instead ``django-mjml``.

**\3\. Set up** ``settings.py`` **in your django project.** ::

  INSTALLED_APPS = (
    ...,
    'mjml',
  )

|

Usage
-----

Load ``mjml`` in your django template and use ``mjml`` tag that will compile mjml to html::

  {% load mjml %}
  
  {% mjml %}
      <mjml>
      <mj-body>
      <mj-container>
          <mj-section>
              <mj-column>
                  <mj-text>Hello world!</mj-text>
              </mj-column>
          </mj-section>
      </mj-container>
      </mj-body>
      </mjml>
  {% endmjml %}

|

Advanced settings
-----------------

There are two backend modes for compiling: ``cmd`` and ``tcpserver``.

**cmd mode**

This mode is very simple, slow and used by default. ::

  MJML_BACKEND_MODE = 'cmd'
  MJML_EXEC_CMD = 'mjml'

You can change ``MJML_EXEC_CMD`` and set path to executable ``mjml`` file, for example::

  MJML_EXEC_CMD = '/home/user/node_modules/.bin/mjml'



**tcpserver mode**

This mode is faster than ``cmd`` but it needs run a server process in background. ::

  MJML_BACKEND_MODE = 'tcpserver'
  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),  # host and port
  ]

You can set several servers and it will be used random one::

  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),
      ('127.0.0.1', 28102),
      ('127.0.0.1', 28103),
  ]

You can run servers by commands::

  # NODE_PATH=/home/user/node_modules node /home/user/.virtualenv/default/lib/python2.7/site-packages/mjml/node/tcpserver.js 28101 127.0.0.1 /tmp/mjmltcpserver.stop

``28101`` - port, ``127.0.0.1`` - host, ``/tmp/mjmltcpserver.stop`` - file that will stop server after touch.

For daemonize server process you can use, for example, supervisor::

  /etc/supervisor/conf.d/mjml.conf

  [program:mjmltcpserver]
  user=user
  environment=NODE_PATH=/home/user/node_modules
  command=node
      /home/user/.virtualenv/default/lib/python2.7/site-packages/mjml/node/tcpserver.js
      28101 127.0.0.1 /tmp/mjmltcpserver.stop
  stdout_logfile=/home/user/project/var/log/supervisor/mjml.log
  autostart=true
  autorestart=true
  redirect_stderr=true
  stopwaitsecs=10
  stopsignal=INT

