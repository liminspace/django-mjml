.. image:: https://github.com/liminspace/django-mjml/actions/workflows/test.yml/badge.svg?branch=master
 :target: https://github.com/liminspace/django-mjml/actions/workflows/test.yml
 :alt: test

.. image:: https://img.shields.io/pypi/v/django-mjml.svg
 :target: https://pypi.org/project/django-mjml/
 :alt: pypi

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

Requirements:
^^^^^^^^^^^^^

* ``Django`` from 1.8 to 3.2
* ``requests`` from 2.20.0 (only if you are going to use API HTTP-server for rendering)
* ``mjml`` from 2.3 to 4.10.1

**\1\. Install** ``mjml``.

See https://github.com/mjmlio/mjml#installation and https://mjml.io/documentation/#installation

**\2\. Install** ``django-mjml``. ::

  $ pip install django-mjml

If you want to use API HTTP-server you also need ``requests`` (at least version 2.20)::

    $ pip install django-mjml[requests]

To install development version use ``git+https://github.com/liminspace/django-mjml.git@master`` instead ``django-mjml``.

**\3\. Set up** ``settings.py`` **in your django project.** ::

  INSTALLED_APPS = (
    ...,
    'mjml',
  )

|

Usage
-----

Load ``mjml`` in your django template and use ``mjml`` tag that will compile MJML to HTML::

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

There are three backend modes for compiling: ``cmd``, ``tcpserver`` and ``httpserver``.

cmd mode
^^^^^^^^

This mode is very simple, slow and used by default. ::

  MJML_BACKEND_MODE = 'cmd'
  MJML_EXEC_CMD = 'mjml'

You can change ``MJML_EXEC_CMD`` and set path to executable ``mjml`` file, for example::

  MJML_EXEC_CMD = '/home/user/node_modules/.bin/mjml'

Also you can pass addition cmd arguments, for example::

  MJML_EXEC_CMD = ['node_modules/.bin/mjml', '--config.minify', 'true', '--config.validationLevel', 'strict']

Once you have a working installation, you can skip the sanity check on startup to speed things up::

  MJML_CHECK_CMD_ON_STARTUP = False

tcpserver mode
^^^^^^^^^^^^^^

This mode is faster than ``cmd`` but it needs run a separated server process which will render templates. ::

  MJML_BACKEND_MODE = 'tcpserver'
  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),  # host and port
  ]

You can set several servers and a random one will be used::

  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),
      ('127.0.0.1', 28102),
      ('127.0.0.1', 28103),
  ]

You can run servers by commands::

  # NODE_PATH=/home/user/node_modules node /home/user/.virtualenv/default/lib/python2.7/site-packages/mjml/node/tcpserver.js --port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop

``28101`` - port, ``127.0.0.1`` - host, ``/tmp/mjmltcpserver.stop`` - file that will stop server after touch.

For daemonize server process you can use, for example, supervisor::

  /etc/supervisor/conf.d/mjml.conf

  [program:mjmltcpserver]
  user=user
  environment=NODE_PATH=/home/user/node_modules
  command=node
      /home/user/.virtualenv/default/lib/python2.7/site-packages/mjml/node/tcpserver.js
      --port=28101 --host=127.0.0.1 --touchstop=/tmp/mjmltcpserver.stop --mjml.minify=true --mjml.validationLevel=strict
  stdout_logfile=/home/user/project/var/log/supervisor/mjml.log
  autostart=true
  autorestart=true
  redirect_stderr=true
  stopwaitsecs=10
  stopsignal=INT

Or you can use docker-compose::

  services:
    mjml-1:
      image: liminspace/mjml-tcpserver:latest
      restart: always
      ports:
        - "28101:28101"

    mjml-2:
      image: liminspace/mjml-tcpserver:latest
      restart: always
      environment:
        HOST: "0.0.0.0"
        PORT: "28102"
        MJML_ARGS: "--mjml.minify=true --mjml.validationLevel=strict"
      expose:
        - "28102"
      ports:
        - "28102:28102"

You also can build your own tcpserver with other versions of ``MJML`` by using
``docker/mjml-tcpserver`` file and editing arguments.

httpserver mode
^^^^^^^^^^^^^^^

  don't forget to install ``requests`` to use this mode.

This mode is faster than ``cmd`` and similar to ``tcpserver`` but you can use official MJML API https://mjml.io/api
or run your own HTTP-server (for example https://github.com/danihodovic/mjml-server) to render templates. ::

  MJML_BACKEND_MODE = 'httpserver'
  MJML_HTTPSERVERS = [
      {
          'URL': 'https://api.mjml.io/v1/render',  # official MJML API
          'HTTP_AUTH': ('<Application ID>', '<Secret Key>'),
      },
      {
          'URL': 'http://127.0.0.1:38101/v1/render',  # your own HTTP-server
      },
  ]

You can set one or more servers and a random one will be used.
