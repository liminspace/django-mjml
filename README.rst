.. image:: https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg
 :target: https://stand-with-ukraine.pp.ua
 :alt: Stand With Ukraine

|

.. image:: https://github.com/liminspace/django-mjml/actions/workflows/test.yml/badge.svg?branch=main
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

* ``Django`` from 2.2 to 6.0
* ``requests`` from 2.24.0 (only if you are going to use API HTTP-server for rendering)
* ``mjml`` from 4.14.1 to 4.17.2 (older version may work, but not tested anymore)

**\1\. Install** ``mjml``.

Follow https://github.com/mjmlio/mjml#installation and https://documentation.mjml.io/#installation to get more info.

**\2\. Install** ``django-mjml``. ::

  $ pip install django-mjml

If you want to use API HTTP-server you also need ``requests`` (at least version 2.24)::

    $ pip install django-mjml[requests]

To install development version use ``git+https://github.com/liminspace/django-mjml.git@main`` instead ``django-mjml``.

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
              <mj-section>
                  <mj-column>
                      <mj-text>Hello world!</mj-text>
                  </mj-column>
              </mj-section>
          </mj-body>
      </mjml>
  {% endmjml %}

|

Advanced settings
-----------------

There are three backend modes for compiling: ``cmd``, ``tcpserver`` and ``httpserver``.

cmd mode
^^^^^^^^

This mode is very simple, slow and used by default.

Configure your Django::

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

This mode is faster than ``cmd`` but it needs the `MJML TCP-Server <https://github.com/liminspace/mjml-tcpserver>`_.

Configure your Django::

  MJML_BACKEND_MODE = 'tcpserver'
  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),  # the host and port of MJML TCP-Server
  ]

You can set several servers and a random one will be used::

  MJML_TCPSERVERS = [
      ('127.0.0.1', 28101),
      ('127.0.0.1', 28102),
      ('127.0.0.1', 28103),
  ]

httpserver mode
^^^^^^^^^^^^^^^

  don't forget to install ``requests`` to use this mode.

This mode is faster than ``cmd`` and a bit slower than ``tcpserver``, but you can use official MJML API https://mjml.io/api
or run your own HTTP-server (for example https://github.com/danihodovic/mjml-server) to render templates.

Configure your Django::

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

Class based backends
^^^^^^^^^^^^^^^^^^^^

All of the modes above are setup as class based backends and we use the same class based backend setup as the django tasks or cache setups.
You can create your own class based backend to handle things like adding extra http headers or authentication when working with http servers
or adding in extra steps in your mjml processes.

To use a class based backend replace your existing MJML django settings with a single MJML setting with the backends you want to setup.
The current template tags require a backend called "default". The BACKEND key is the import path to the backend you want to use
The OPTIONS key provides specific configuration for that backend.

  MJML = {
    "default": {
      "BACKEND": "myapp.mjml.backends.MySpecialBackend"
      "OPTIONS": {
        "check_on_startup": False
      }
    }
  }


Provided Class based Backends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each mode covered above has its own class base backend provided by django-mjml

  cmd - mjml.backends.cmd.CmdBackend
  httpserver - mjml.backends.http.HttpBackend
  tcpserver - mjml.backends.tcp.TcpBackend


Each on has its own options that align with the existing options available along with options available to all backends


global options

  check_on_startup: When loading the backends run a check on the backend to see if it can render.
    This will raise an exception and stop your app starting up if it fails


mjml.backends.cmd.CmdBackend

  exec_cmd: The path to the mjml cli or an extended command provided as a list

mjml.backends.http.HttpBackend

  servers: The details of the servers to send the render requests to provided as a list
    each item in the list is a dict with the following
      urL: the url to send the render request to
      auth: an optional tuple with the username first and password second

mjml.backends.tcp.TcpBackend
  servers: A list of tuples with the ip/hostname first and the port second (as an integer)


Writing your own Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can crete your own backend using the mjml.backends.base.BaseBackend
Inherit this class and then add your own render method to do what you need to do.

When you are ready to test it out change the MJML["default"]["BACKEND"] django setting to your new class
and set the OPTIONS as you need to